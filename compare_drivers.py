"""
compare_drivers.py  –  Fetch and compare lap times for any two drivers.

Usage:
    python compare_drivers.py                 # defaults: driver 1 vs 16
    python compare_drivers.py 44 16           # Hamilton vs Leclerc
"""

import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_URL   = "https://api.openf1.org/v1"
SESSION_KEY = 9158          # Monaco 2024 Race


def fetch_laps(driver_number: int) -> list:
    url = f"{BASE_URL}/laps?session_key={SESSION_KEY}&driver_number={driver_number}"
    print(f"  Fetching laps for driver #{driver_number} …")
    try:
        req = Request(url, headers={"User-Agent": "OpenF1-Student/1.0"})
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (HTTPError, URLError) as e:
        print(f"  ✗ Error: {e}")
        return []


def build_lap_map(laps: list) -> dict:
    """Return {lap_number: lap_duration} ignoring laps without a valid time."""
    return {
        lap["lap_number"]: lap["lap_duration"]
        for lap in laps
        if lap.get("lap_duration") is not None
    }


def compare(d1: int, d2: int):
    laps1 = fetch_laps(d1)
    laps2 = fetch_laps(d2)

    map1 = build_lap_map(laps1)
    map2 = build_lap_map(laps2)

    common = sorted(set(map1) & set(map2))
    if not common:
        print("  No common lap data found."); return

    print(f"\n{'─'*62}")
    print(f"  Lap comparison  –  Driver #{d1} vs Driver #{d2}")
    print(f"  Session: Monaco GP 2024 Race (key {SESSION_KEY})")
    print(f"{'─'*62}")
    print(f"  {'Lap':>3}  {'Driver '+str(d1):>12}  {'Driver '+str(d2):>12}  "
          f"{'Diff (s)':>10}  Winner")
    print(f"  {'─'*3}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*8}")

    d1_wins = d2_wins = 0
    for lap in common:
        t1, t2 = map1[lap], map2[lap]
        diff   = round(t2 - t1, 3)
        winner = f"#{d1}" if diff > 0 else (f"#{d2}" if diff < 0 else "Tie")
        if diff > 0:   d1_wins += 1
        elif diff < 0: d2_wins += 1
        print(f"  {lap:>3}  {t1:>12.3f}  {t2:>12.3f}  {diff:>+10.3f}  {winner}")

    print(f"{'─'*62}")
    print(f"  Laps won  →  #{d1}: {d1_wins}   #{d2}: {d2_wins}   Ties: {len(common)-d1_wins-d2_wins}")

    # Best laps
    best1 = min(map1.values())
    best2 = min(map2.values())
    faster = d1 if best1 < best2 else d2
    print(f"  Best lap  →  #{d1}: {best1:.3f}s  |  #{d2}: {best2:.3f}s  |  Faster: #{faster}")
    print()


if __name__ == "__main__":
    d1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    d2 = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    compare(d1, d2)
