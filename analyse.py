"""
analyse.py  –  Quick analysis of saved OpenF1 JSON data.

Run AFTER fetch_data.py has created the data/ folder.
"""

import json
import os

DATA_DIR = "data"


def load(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


# ─────────────────────────────────────────────────────────────────────────────

def analyse_drivers():
    section("🏎  DRIVERS")
    data = load("drivers.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'#':>3}  {'Name':<25}  {'Team':<30}  Code")
    print(f"  {'─'*3}  {'─'*25}  {'─'*30}  {'─'*4}")
    for d in data:
        print(f"  {d.get('driver_number','-'):>3}  "
              f"{d.get('full_name','-'):<25}  "
              f"{d.get('team_name','-'):<30}  "
              f"{d.get('name_acronym','-')}")


def analyse_positions():
    section("📍 POSITIONS")
    data = load("positions.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'Pos':>3}  {'Driver #':>8}  Date")
    for p in data:
        print(f"  {p.get('position','-'):>3}  {p.get('driver_number','-'):>8}  "
              f"{p.get('date','-')}")


def analyse_sessions():
    section("🗓  SESSIONS")
    data = load("sessions.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    for s in data:
        print(f"  [{s.get('session_key','-')}] {s.get('session_name','-'):<20} "
              f"{s.get('location','-')}, {s.get('country_name','-')}")


def analyse_weather():
    section("🌤  WEATHER  (track conditions over time)")
    data = load("weather.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'Time':<26}  {'Air °C':>6}  {'Track °C':>8}  {'Wind km/h':>9}  {'Rain':>4}")
    for w in data:
        print(f"  {w.get('date','-'):<26}  "
              f"{w.get('air_temperature','-'):>6}  "
              f"{w.get('track_temperature','-'):>8}  "
              f"{w.get('wind_speed','-'):>9}  "
              f"{w.get('rainfall','-'):>4}")


def analyse_laps():
    section("⏱  LAPS  (driver 16 – Charles Leclerc)")
    data = load("laps.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'Lap':>3}  {'Lap Time':>10}  {'S1':>8}  {'S2':>8}  {'S3':>8}  {'Top Speed':>9}")
    for lap in data:
        print(f"  {lap.get('lap_number','-'):>3}  "
              f"{str(lap.get('lap_duration','-')):>10}  "
              f"{str(lap.get('duration_sector_1','-')):>8}  "
              f"{str(lap.get('duration_sector_2','-')):>8}  "
              f"{str(lap.get('duration_sector_3','-')):>8}  "
              f"{str(lap.get('i2_speed','-')):>9}")


def analyse_pit_stops():
    section("🔧 PIT STOPS")
    data = load("pit_stops.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'Driver':>6}  {'Lap':>3}  {'Stop #':>6}  {'Duration (s)':>12}")
    for p in data:
        print(f"  {p.get('driver_number','-'):>6}  "
              f"{p.get('lap_number','-'):>3}  "
              f"{p.get('pit_out_time','-')!s:>6}  "
              f"{p.get('stop_duration','-'):>12}")


def analyse_race_control():
    section("🚩 RACE CONTROL MESSAGES")
    data = load("race_control.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    for msg in data:
        flag    = msg.get('flag', '')
        category = msg.get('category', '')
        message  = msg.get('message', '')
        t        = msg.get('date', '')[:19]
        print(f"  [{t}] {flag:>10}  {category:<18}  {message[:60]}")


def analyse_intervals():
    section("📏 INTERVALS (gap to car ahead / leader)")
    data = load("intervals.json")
    if not data:
        print("  No data – run fetch_data.py first"); return
    print(f"  {'Driver':>6}  {'Gap ahead':>10}  {'Gap leader':>10}")
    for i in data:
        print(f"  {i.get('driver_number','-'):>6}  "
              f"{str(i.get('interval','-')):>10}  "
              f"{str(i.get('gap_to_leader','-')):>10}")


# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 55)
    print("  OpenF1 Data Analysis  |  Monaco GP 2024 – Race")
    print("=" * 55)

    analyse_drivers()
    analyse_positions()
    analyse_sessions()
    analyse_weather()
    analyse_laps()
    analyse_pit_stops()
    analyse_race_control()
    analyse_intervals()

    print("\n" + "=" * 55)
    print("  Analysis complete.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
