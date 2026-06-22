"""
OpenF1 Data Explorer - Member 3: Data Exploration
Fetches sample data from multiple OpenF1 API endpoints and saves as JSON.

Endpoints covered:
  Original  : drivers, position, sessions
  Extended  : weather, laps, pit_stops, race_control, intervals
"""

import json
import os
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_URL = "https://api.openf1.org/v1"
DATA_DIR = "data"
# Monaco 2024 Race session – a reliable historical session key
SESSION_KEY = 9158


# ── helpers ──────────────────────────────────────────────────────────────────

def fetch(endpoint: str, params: dict = None) -> list:
    """Fetch JSON from an OpenF1 endpoint with optional query params."""
    url = f"{BASE_URL}/{endpoint}?session_key={SESSION_KEY}"
    if params:
        for k, v in params.items():
            url += f"&{k}={v}"

    print(f"  GET {url}")
    try:
        req = Request(url, headers={"User-Agent": "OpenF1-Student/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            # Trim to first 5 records to keep files small
            return data[:5] if isinstance(data, list) else data
    except HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.reason}")
        return []
    except URLError as e:
        print(f"  ✗ URL Error: {e.reason}")
        return []


def save(filename: str, data) -> None:
    """Save data as a pretty-printed JSON file inside data/."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved → {path}  ({len(data)} records)\n")


# ── endpoint fetchers ─────────────────────────────────────────────────────────

def fetch_drivers():
    print("📋 Fetching DRIVERS ...")
    data = fetch("drivers")
    save("drivers.json", data)
    return data


def fetch_positions():
    print("📍 Fetching POSITIONS ...")
    data = fetch("position")
    save("positions.json", data)
    return data


def fetch_sessions():
    print("🗓  Fetching SESSIONS ...")
    data = fetch("sessions")
    save("sessions.json", data)
    return data


# ── extended endpoints (new) ──────────────────────────────────────────────────

def fetch_weather():
    print("🌤  Fetching WEATHER ...")
    data = fetch("weather")
    save("weather.json", data)
    return data


def fetch_laps():
    """Fetch first 5 laps for driver 16 (Charles Leclerc)."""
    print("⏱  Fetching LAPS (driver 16) ...")
    data = fetch("laps", {"driver_number": 16})
    save("laps.json", data)
    return data


def fetch_pit_stops():
    print("🔧 Fetching PIT STOPS ...")
    data = fetch("pit")
    save("pit_stops.json", data)
    return data


def fetch_race_control():
    print("🚩 Fetching RACE CONTROL messages ...")
    data = fetch("race_control")
    save("race_control.json", data)
    return data


def fetch_intervals():
    print("📏 Fetching INTERVALS (gaps between cars) ...")
    data = fetch("intervals")
    save("intervals.json", data)
    return data


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  OpenF1 Data Explorer  |  Session Key:", SESSION_KEY)
    print("  Monaco GP 2024 – Race")
    print("=" * 60, "\n")

    results = {}

    # Original 3
    results["drivers"]      = fetch_drivers();      time.sleep(0.5)
    results["positions"]    = fetch_positions();    time.sleep(0.5)
    results["sessions"]     = fetch_sessions();     time.sleep(0.5)

    # Extended 5
    results["weather"]      = fetch_weather();      time.sleep(0.5)
    results["laps"]         = fetch_laps();         time.sleep(0.5)
    results["pit_stops"]    = fetch_pit_stops();    time.sleep(0.5)
    results["race_control"] = fetch_race_control(); time.sleep(0.5)
    results["intervals"]    = fetch_intervals();    time.sleep(0.5)

    print("=" * 60)
    print("  All done!  Files saved to data/")
    print("  Run  python analyse.py  to see a quick summary.")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
