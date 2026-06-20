

from datetime import datetime, timezone
from weather_forecast import get_race_weather, CIRCUIT_COORDS, WeatherFetchError


def build_race_features(driver_row: dict, circuit_name: str, race_datetime: datetime) -> dict:
    """
    Takes an existing row of driver/race features (grid position, constructor
    points, etc.) and enriches it with live weather features.
    """
    lat, lon = CIRCUIT_COORDS[circuit_name]

    try:
        weather = get_race_weather(lat, lon, race_datetime=race_datetime)
    except WeatherFetchError as e:
        print(f"Warning: weather fetch failed ({e}). Falling back to defaults.")
        weather = {
            "temp_c": 20.0, "humidity_pct": 50.0, "wind_speed_ms": 3.0,
            "rain_probability": 0.0, "rain_volume_mm": 0.0,
            "cloud_cover_pct": 20.0, "is_wet_race_risk": False,
        }

    enriched_row = {
        **driver_row,
        "weather_temp_c": weather["temp_c"],
        "weather_humidity_pct": weather["humidity_pct"],
        "weather_wind_speed_ms": weather["wind_speed_ms"],
        "weather_rain_probability": weather.get("rain_probability") or 0.0,
        "weather_rain_volume_mm": weather["rain_volume_mm"],
        "weather_cloud_cover_pct": weather["cloud_cover_pct"],
        "weather_is_wet_risk": int(weather["is_wet_race_risk"]),
    }
    return enriched_row


if __name__ == "__main__":
    sample_driver_row = {
        "driver": "Max Verstappen",
        "grid_position": 1,
        "constructor_points": 450,
        "driver_form_last5": 1.2,
    }

    race_time = datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc)  # example Spa race time

    full_row = build_race_features(sample_driver_row, "spa", race_time)
    print(full_row)