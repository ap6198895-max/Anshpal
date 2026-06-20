"""
FastF1 -> Elo Rating loader
------------------------------
Pulls race results from FastF1, season by season, and feeds them into
the EloRatingSystem in chronological order so ratings evolve correctly
over time.

Usage:
    from elo_rating import EloRatingSystem
    from elo_fastf1_loader import enable_fastf1_cache, build_elo_ratings_for_seasons

    enable_fastf1_cache()
    elo, history_df = build_elo_ratings_for_seasons([2022, 2023, 2024])

    print(elo.ratings_table()[:10])      # current top 10 drivers by rating
    print(history_df.tail(20))           # rating changes over time
"""

import os
import fastf1
import pandas as pd

from elo_rating import EloRatingSystem, EloConfig


def enable_fastf1_cache(cache_dir: str = "./fastf1_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)


# Status values that count as "classified finisher" for ordering purposes,
# even if not literally "Finished" (e.g. lapped cars still get a real
# finishing position). Only count clear DNF causes as DNFs.
_DNF_STATUS_KEYWORDS = (
    "Accident", "Collision", "Crash", "Retired", "Engine", "Gearbox",
    "Hydraulics", "Mechanical", "Electrical", "Suspension", "Brakes",
    "Did not finish", "DNF", "Withdrew", "Disqualified", "Excluded",
)


def _is_dnf(status: str) -> bool:
    if not isinstance(status, str):
        return False
    return any(keyword.lower() in status.lower() for keyword in _DNF_STATUS_KEYWORDS)


def get_race_finishing_order(year: int, event) -> tuple[list[str], set[str]]:
    """
    Fetch one race's results from FastF1 and return:
        (finishing_order, dnf_driver_ids)

    finishing_order is a list of driver abbreviations (e.g. "VER") ordered
    from 1st to last classified position. Drivers with completely missing
    position data (known FastF1 data gaps in some 2025 races) are dropped
    with a printed warning rather than breaking the whole batch run.
    """
    session = fastf1.get_session(year, event, "R")
    session.load(laps=False, telemetry=False, weather=False)

    results = session.results
    if results is None or results.empty:
        raise ValueError(f"No race results found for {year} {event}")

    df = results[["Abbreviation", "Position", "ClassifiedPosition", "Status"]].copy()

    # Prefer Position; fall back to ClassifiedPosition if Position is NaN
    # (handles the known FastF1 gap where Position is sometimes all-NaN)
    df["SortKey"] = pd.to_numeric(df["Position"], errors="coerce")
    fallback = pd.to_numeric(df["ClassifiedPosition"], errors="coerce")
    df["SortKey"] = df["SortKey"].fillna(fallback)

    missing = df[df["SortKey"].isna()]
    if not missing.empty:
        print(f"Warning: dropping {len(missing)} driver(s) with no usable "
              f"position data in {year} {event}: {list(missing['Abbreviation'])}")
    df = df.dropna(subset=["SortKey"]).sort_values("SortKey")

    finishing_order = df["Abbreviation"].tolist()
    dnf_drivers = set(df.loc[df["Status"].apply(_is_dnf), "Abbreviation"])

    return finishing_order, dnf_drivers


def build_elo_ratings_for_seasons(years: list[int], config: EloConfig = None,
                                   skip_on_error: bool = True):
    """
    Process every race across the given seasons, in chronological order,
    updating a single EloRatingSystem throughout.

    Args:
        years: List of season years to include, e.g. [2022, 2023, 2024].
        config: Optional EloConfig to customize K-factor, DNF penalty, etc.
        skip_on_error: If True, races that fail to load (network issues,
                        FastF1 data gaps) are skipped with a warning instead
                        of stopping the whole run.

    Returns:
        (EloRatingSystem instance, history DataFrame)
    """
    elo = EloRatingSystem(config)

    for year in sorted(years):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        races = schedule.sort_values("RoundNumber")

        for _, event_row in races.iterrows():
            event_name = event_row["EventName"]
            race_id = f"{year}_{event_name.replace(' ', '_')}"
            try:
                finishing_order, dnf_drivers = get_race_finishing_order(year, event_name)
                if len(finishing_order) < 2:
                    print(f"Skipping {race_id}: fewer than 2 classified drivers")
                    continue
                elo.process_race(race_id, finishing_order, dnf_drivers)
            except Exception as e:
                msg = f"Skipping {race_id}: {e}"
                if skip_on_error:
                    print(f"Warning: {msg}")
                    continue
                raise RuntimeError(msg) from e

    return elo, elo.history_dataframe()


def get_elo_features(elo: EloRatingSystem) -> pd.DataFrame:
    """
    Convert current Elo ratings into a model-ready feature DataFrame:
    one row per driver with their current rating and race count.
    """
    rows = [
        {"Driver": driver, "elo_rating": rating, "elo_races_completed": elo.races_completed[driver]}
        for driver, rating in elo.ratings_table()
    ]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    enable_fastf1_cache()

    elo, history = build_elo_ratings_for_seasons([2023, 2024])

    print("Current Elo ratings (top 10):")
    for driver, rating in elo.ratings_table()[:10]:
        print(f"  {driver}: {rating:.1f}")

    print("\nModel-ready feature table:")
    print(get_elo_features(elo))
