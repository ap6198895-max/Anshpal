"""
live_leaderboard.py  –  Poll the OpenF1 API every N seconds and print
                         a live race leaderboard in the terminal.

Usage:
    python live_leaderboard.py              # refresh every 5 s
    python live_leaderboard.py 10           # refresh every 10 s
    Ctrl+C to stop.

NOTE: For LIVE data you need a paid OpenF1 subscription.
      During a historical session the snapshot is static but the script
      structure shows how a real live dashboard would work.
"""

import json
import os
import sys
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_URL    = "https://api.openf1.org/v1"
SESSION_KEY = 9158          # Monaco 2024 Race (historical – always available)
REFRESH     = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def fetch(endpoint: str, extra: str = "") -> list:
    url = f"{BASE_URL}/{endpoint}?session_key={SESSION_KEY}{extra}"
    try:
        req = Request(url, headers={"User-Agent": "OpenF1-Live/1.0"})
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except (HTTPError, URLError):
        return []


def get_leaderboard():
    """Combine /position and /drivers into a leaderboard list."""
    positions = fetch("position")
    drivers   = fetch("drivers")

    # Build driver lookup: driver_number → name/team
    driver_map = {
        d["driver_number"]: {
            "name":  d.get("full_name", "Unknown"),
            "code":  d.get("name_acronym", "???"),
            "team":  d.get("team_name", ""),
            "color": d.get("team_colour", "FFFFFF"),
        }
        for d in drivers
    }

    # Get latest position per driver (API returns history; take first unique)
    seen   = set()
    board  = []
    for p in positions:
        dn = p.get("driver_number")
        if dn in seen:
            continue
        seen.add(dn)
        info = driver_map.get(dn, {"name": f"#{dn}", "code": "???", "team": "", "color": ""})
        board.append({
            "pos":    p.get("position", 99),
            "driver": dn,
            "code":   info["code"],
            "name":   info["name"],
            "team":   info["team"],
        })

    board.sort(key=lambda x: x["pos"])
    return board


def get_weather_snapshot():
    weather = fetch("weather")
    if not weather:
        return {}
    latest = weather[-1]          # most recent record
    return {
        "air":   latest.get("air_temperature", "–"),
        "track": latest.get("track_temperature", "–"),
        "wind":  latest.get("wind_speed", "–"),
        "rain":  latest.get("rainfall", 0),
    }


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_leaderboard(board, weather, iteration):
    clear_screen()
    now = datetime.now().strftime("%H:%M:%S")

    print("╔" + "═"*52 + "╗")
    print(f"║  🏎  OpenF1 LIVE LEADERBOARD  |  {now}  refresh #{iteration}  ║")
    print("╠" + "═"*52 + "╣")
    print(f"║  Session: Monaco GP 2024 (key {SESSION_KEY})              ║")
    if weather:
        rain_icon = "🌧" if weather.get("rain", 0) else "☀️ "
        print(f"║  {rain_icon} Air: {weather['air']}°C  "
              f"Track: {weather['track']}°C  "
              f"Wind: {weather['wind']} km/h     ║")
    print("╠" + "═"*52 + "╣")
    print(f"║  {'P':>2}  {'Code':<5}  {'Driver':<22}  {'Team':<18} ║")
    print("╠" + "═"*52 + "╣")
    for row in board[:20]:        # top 20
        line = (f"  {row['pos']:>2}  {row['code']:<5}  "
                f"{row['name'][:22]:<22}  {row['team'][:18]:<18}")
        print(f"║{line} ║")
    print("╚" + "═"*52 + "╝")
    print(f"  Next refresh in {REFRESH}s  |  Ctrl+C to stop")


def main():
    print(f"Starting live leaderboard (refresh={REFRESH}s) …")
    iteration = 1
    try:
        while True:
            board   = get_leaderboard()
            weather = get_weather_snapshot()
            print_leaderboard(board, weather, iteration)
            iteration += 1
            time.sleep(REFRESH)
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
