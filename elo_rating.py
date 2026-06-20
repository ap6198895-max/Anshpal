"""
F1 Driver Elo Rating System — core engine
-------------------------------------------
Standard chess-style Elo, adapted for multi-driver races using pairwise
updates: every pair of drivers in a race is treated as a mini head-to-head
match based on who finished ahead of whom.

This module is data-source agnostic — it only needs an ordered list of
driver IDs per race (best to worst finish). See elo_fastf1_loader.py for
the FastF1-specific data loading.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


DEFAULT_RATING = 1500.0


@dataclass
class EloConfig:
    k_factor: float = 16.0          # update step size; lower = more stable, slower to adapt
    dnf_penalty: float = 0.5        # score awarded to a DNF driver vs a finisher (0=loss, 0.5=draw)
    rookie_k_multiplier: float = 1.5  # extra K-factor boost for drivers with few races (faster calibration)
    rookie_race_threshold: int = 10   # below this many career races, rookie multiplier applies


class EloRatingSystem:
    """
    Maintains and updates Elo ratings for F1 drivers across a season (or
    multiple seasons) of races.
    """

    def __init__(self, config: Optional[EloConfig] = None):
        self.config = config or EloConfig()
        self.ratings: dict[str, float] = defaultdict(lambda: DEFAULT_RATING)
        self.races_completed: dict[str, int] = defaultdict(int)
        self.history: list[dict] = []  # one row per (race, driver) snapshot

    def get_rating(self, driver_id: str) -> float:
        return self.ratings[driver_id]

    def _k_for(self, driver_id: str) -> float:
        k = self.config.k_factor
        if self.races_completed[driver_id] < self.config.rookie_race_threshold:
            k *= self.config.rookie_k_multiplier
        return k

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

    def process_race(self, race_id: str, finishing_order: list[str],
                      dnf_drivers: Optional[set[str]] = None) -> dict[str, float]:
        """
        Update ratings based on one race's results.

        Args:
            race_id: Unique identifier for the race (e.g. "2024_Monaco").
            finishing_order: Driver IDs ordered from 1st to last classified
                              finisher (DNFs should still be included, placed
                              at their classified position — typically last).
            dnf_drivers: Set of driver IDs who DNF'd in this race. Their
                         pairwise results vs classified finishers use
                         dnf_penalty instead of a clean loss, since a DNF
                         isn't always a pure skill signal (mechanical failure
                         vs driver error vs crash caused by someone else).

        Returns:
            Dict of driver_id -> new rating, for drivers in this race.
        """
        dnf_drivers = dnf_drivers or set()
        n = len(finishing_order)
        if n < 2:
            return {d: self.ratings[d] for d in finishing_order}

        # Accumulate rating deltas, apply all at once after computing every
        # pairwise comparison (so order within the race doesn't bias updates)
        deltas = defaultdict(float)
        pair_count = defaultdict(int)

        for i in range(n):
            for j in range(i + 1, n):
                driver_ahead = finishing_order[i]
                driver_behind = finishing_order[j]

                rating_ahead = self.ratings[driver_ahead]
                rating_behind = self.ratings[driver_behind]

                expected_ahead = self._expected_score(rating_ahead, rating_behind)
                expected_behind = 1.0 - expected_ahead

                # Actual score: 1.0 for a clean win (finished ahead, both classified).
                # If the trailing driver DNF'd, soften the "win" toward 0.5 using
                # dnf_penalty, since a DNF is a weaker skill signal than a clean
                # loss (could be mechanical failure, contact caused by someone
                # else, etc.) — dnf_penalty=0.5 means "treat as a draw",
                # dnf_penalty=0.0 means "treat exactly like a normal loss".
                if driver_behind in dnf_drivers and driver_ahead not in dnf_drivers:
                    actual_ahead = 1.0 - (1.0 - self.config.dnf_penalty) * 0.5
                else:
                    actual_ahead = 1.0
                actual_behind = 1.0 - actual_ahead

                k_ahead = self._k_for(driver_ahead)
                k_behind = self._k_for(driver_behind)

                deltas[driver_ahead] += k_ahead * (actual_ahead - expected_ahead)
                deltas[driver_behind] += k_behind * (actual_behind - expected_behind)
                pair_count[driver_ahead] += 1
                pair_count[driver_behind] += 1

        # Average each driver's accumulated delta over the number of
        # pairwise comparisons they were part of, so ratings don't blow up
        # in races with more drivers (20 drivers = 190 pairs)
        new_ratings = {}
        for driver in finishing_order:
            avg_delta = deltas[driver] / pair_count[driver] if pair_count[driver] else 0.0
            self.ratings[driver] += avg_delta
            self.races_completed[driver] += 1
            new_ratings[driver] = self.ratings[driver]

            self.history.append({
                "race_id": race_id,
                "driver_id": driver,
                "rating_before": self.ratings[driver] - avg_delta,
                "rating_after": self.ratings[driver],
                "delta": avg_delta,
                "dnf": driver in dnf_drivers,
            })

        return new_ratings

    def ratings_table(self):
        """Return current ratings as a sorted list of (driver_id, rating) tuples, highest first."""
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)

    def history_dataframe(self):
        """Return the full update history as a pandas DataFrame, if pandas is available."""
        import pandas as pd
        return pd.DataFrame(self.history)
