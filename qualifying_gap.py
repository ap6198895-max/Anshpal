"""
Qualifying Gap-to-Pole Feature Extractor (FastF1)
---------------------------------------------------
Grid position alone loses information: P2 might be 0.05s off pole or
0.8s off pole, and those are very different signals for race pace.
This module pulls real Q1/Q2/Q3 times from FastF1 and converts them
into gap-to-pole features (in seconds) for each driver.

Setup:
    pip install fastf1

Usage:
    from qualifying_gap import get_qualifying_gaps

    df = get_qualifying_gaps(2024, "Monaco")
    print(df)
"""

import fastf1
import pandas as pd


def enable_fastf1_cache(cache_dir: str = "./fastf1_cache"):
    """
    Enable local caching so repeated loads don't re-download session data.
    Call this once at the start of your script.
    """
    import os
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)


def get_qualifying_gaps(year: int, event, session_type: str = "Q") -> pd.DataFrame:
    """
    Fetch qualifying results for an event and compute each driver's gap
    to pole position, both overall and per-segment (Q1/Q2/Q3).

    Args:
        year: Season year, e.g. 2024.
        event: Event name (e.g. "Monaco") or round number (e.g. 7).
        session_type: "Q" for normal qualifying, "SQ" for sprint qualifying.

    Returns:
        DataFrame with one row per driver:
            Driver, Team, Position, Q1, Q2, Q3,
            BestTime, GapToPole_s, GapToPole_pct,
            Q1_GapToPole_s, Q2_GapToPole_s, Q3_GapToPole_s
        Times are in seconds (float). Drivers who didn't set a time in a
        segment (eliminated earlier) have NaN for that segment's gap.
    """
    session = fastf1.get_session(year, event, session_type)
    session.load(laps=False, telemetry=False, weather=False)  # results only, faster load

    results = session.results
    if results is None or results.empty:
        raise ValueError(f"No qualifying results found for {year} {event}")

    df = results[["Abbreviation", "TeamName", "Position", "Q1", "Q2", "Q3"]].copy()
    df = df.rename(columns={"Abbreviation": "Driver", "TeamName": "Team"})

    # Convert Timedelta columns to seconds (float), NaT -> NaN
    for col in ["Q1", "Q2", "Q3"]:
        df[col] = df[col].dt.total_seconds()

    # Each driver's best time across whichever segments they ran
    df["BestTime"] = df[["Q1", "Q2", "Q3"]].min(axis=1)

    pole_time = df["BestTime"].min()
    if pd.isna(pole_time):
        raise ValueError(f"Could not determine pole time for {year} {event} — no valid lap times found")

    df["GapToPole_s"] = df["BestTime"] - pole_time
    df["GapToPole_pct"] = (df["GapToPole_s"] / pole_time) * 100

    # Per-segment gap to that segment's own best time (useful for tracking
    # who was sandbagging vs pushing in each phase)
    for seg in ["Q1", "Q2", "Q3"]:
        seg_best = df[seg].min()
        df[f"{seg}_GapToPole_s"] = df[seg] - seg_best if pd.notna(seg_best) else pd.NA

    df = df.sort_values("Position").reset_index(drop=True)
    return df


def build_qualifying_features(year: int, event, session_type: str = "Q") -> pd.DataFrame:
    """
    Slimmed-down version of get_qualifying_gaps() returning just the
    columns most useful as model features, ready to merge into your
    main feature table on "Driver".
    """
    df = get_qualifying_gaps(year, event, session_type)
    return df[[
        "Driver", "Team", "Position",
        "GapToPole_s", "GapToPole_pct",
        "Q3_GapToPole_s",
    ]].rename(columns={
        "Position": "grid_position_quali",  # note: final grid can differ due to penalties
        "GapToPole_s": "quali_gap_to_pole_s",
        "GapToPole_pct": "quali_gap_to_pole_pct",
        "Q3_GapToPole_s": "quali_q3_gap_s",
    })


if __name__ == "__main__":
    enable_fastf1_cache()

    gaps = get_qualifying_gaps(2024, "Monaco")
    print(gaps[["Driver", "Team", "Position", "BestTime", "GapToPole_s", "GapToPole_pct"]])

    print("\nModel-ready features:")
    print(build_qualifying_features(2024, "Monaco"))
