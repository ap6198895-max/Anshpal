# OpenF1 API Notes
**Session used for samples:** Monaco GP 2024 – Race (`session_key = 9158`)
**Base URL:** `https://api.openf1.org/v1`

---

## Endpoint Reference

| Endpoint | Purpose | Important Fields | Example Response |
|---|---|---|---|
| `drivers` | Get all driver info for a session | `driver_number`, `full_name`, `team_name`, `name_acronym`, `team_colour` | `{"driver_number": 16, "full_name": "Charles Leclerc", ...}` |
| `position` | Live driver positions (updated ~every 0.1 s) | `position`, `driver_number`, `date` | `{"position": 1, "driver_number": 4, "gap": "0.000", ...}` |
| `sessions` | Session metadata (Practice, Quali, Race, Sprint) | `session_key`, `session_name`, `location`, `country_name`, `date_start` | `{"session_key": 9158, "location": "Monaco", ...}` |
| `weather` | Track weather, updated every minute | `air_temperature`, `track_temperature`, `wind_speed`, `wind_direction`, `rainfall`, `humidity` | `{"air_temperature": 26.8, "rainfall": 0, ...}` |
| `laps` | Per-lap timing data per driver | `lap_number`, `lap_duration`, `duration_sector_1/2/3`, `i2_speed` (speed trap), `is_pit_out_lap` | `{"lap_number": 1, "lap_duration": 108.372, ...}` |
| `pit` | Pit stop events | `driver_number`, `lap_number`, `pit_duration`, `date` | `{"driver_number": 16, "lap_number": 27, "pit_duration": 22.1, ...}` |
| `race_control` | Official messages: flags, safety car, DRS, incidents | `flag`, `category`, `message`, `date`, `driver_number`, `lap_number` | `{"flag": "YELLOW", "category": "Flag", "message": "ACCIDENT ...", ...}` |
| `intervals` | Gap to car ahead & gap to leader (race only) | `driver_number`, `interval`, `gap_to_leader`, `date` | `{"driver_number": 16, "interval": 0.337, "gap_to_leader": 0.0, ...}` |

---

## Detailed Notes

### `/drivers`
- Returns one entry **per driver per session** – same driver appears in multiple sessions.
- `team_colour` is a hex string (e.g. `"E8002D"` for Ferrari).
- Filter example: `?session_key=9158&driver_number=16`

### `/position`
- High-frequency endpoint (~10 Hz during a session).
- Iterate through results and take the **latest record per driver** for a current snapshot.
- Filter by time: `?session_key=9158&date>2024-05-26T14:00:00`

### `/sessions`
- Use `session_type` field to distinguish `"Race"`, `"Qualifying"`, `"Practice 1"` etc.
- `date_start` and `date_end` are ISO 8601 UTC strings.

### `/weather`
- `rainfall` is an **integer**, not boolean: `0 = dry`, higher values = wetter.
- Updates roughly every 60 seconds.

### `/laps`
- `lap_duration = None` for in-laps / formation laps – always guard against `None`.
- `is_pit_out_lap: true` marks the out-lap after a pit stop.
- Sector times in seconds (floats).

### `/pit`
- `pit_duration` is stop time in seconds (tyres + stationary time).
- Does **not** include in-lap or out-lap time.

### `/race_control`
- `flag` values: `"GREEN"`, `"YELLOW"`, `"RED"`, `"CHEQUERED"`, `"CLEAR"`, `"DOUBLE YELLOW"`.
- `category`: `"Flag"`, `"Drs"`, `"SafetyCar"`, `"Other"`.
- Filter by flag: `?session_key=9158&flag=YELLOW`

### `/intervals`
- Only populated **during the race** (not practice/qualifying).
- `interval` is the gap to the car directly ahead.
- `gap_to_leader` is the cumulative gap to P1.

---

## Useful Query Tricks

```bash
# All laps for one driver
https://api.openf1.org/v1/laps?session_key=9158&driver_number=16

# Only yellow flag messages
https://api.openf1.org/v1/race_control?session_key=9158&flag=YELLOW

# Pit stops under 3 seconds (very fast stop)
https://api.openf1.org/v1/pit?session_key=9158&pit_duration<3

# Weather at a specific time range
https://api.openf1.org/v1/weather?session_key=9158&date>2024-05-26T13:00:00

# Intervals for leader only (gap_to_leader = 0)
https://api.openf1.org/v1/intervals?session_key=9158&gap_to_leader=0
```

---

## Scripts in This Project

| File | What it does |
|---|---|
| `fetch_data.py` | Fetches all 8 endpoints and saves JSON to `data/` |
| `analyse.py` | Reads saved JSON and prints formatted tables |
| `compare_drivers.py` | Compares lap-by-lap times for any two drivers |
| `live_leaderboard.py` | Polls the API every N seconds and shows a live leaderboard |

---

*End Goal: The team clearly understands where each piece of live race data comes from.*
