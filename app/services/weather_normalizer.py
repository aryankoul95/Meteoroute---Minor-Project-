from typing import Optional


def normalize_weather(
    weather: dict,
) -> dict:
    """
    Convert weather data from the Open-Meteo client
    into a consistent MeteoRoute weather format.
    """

    return {
        "latitude": float(
            weather.get("latitude", 0.0)
        ),

        "longitude": float(
            weather.get("longitude", 0.0)
        ),

        "distance_from_start_km": float(
            weather.get(
                "distance_from_start_km",
                0.0,
            )
        ),

        "estimated_arrival_minutes": float(
            weather.get(
                "estimated_arrival_minutes",
                0.0,
            )
        ),

        "forecast_time": weather.get(
            "forecast_time"
        ),

        "temperature_c": _to_float(
            weather.get("temperature_c")
        ),

        "wind_speed_kmh": _to_float(
            weather.get("wind_speed_kmh")
        ),

        "wind_gust_kmh": _to_float(
            weather.get("wind_gust_kmh")
        ),

        "precipitation_mm": _to_float(
            weather.get("precipitation_mm")
        ),

        "weather_code": _to_int(
            weather.get("weather_code")
        ),

        "source": weather.get(
            "weather_source",
            "Open-Meteo",
        ),
    }


def _to_float(
    value: Optional[float],
) -> Optional[float]:

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def _to_int(
    value: Optional[int],
) -> Optional[int]:

    if value is None:
        return None

    try:
        return int(value)

    except (TypeError, ValueError):
        return None


def normalize_weather_batch(
    weather_data: list[dict],
) -> list[dict]:
    """
    Normalize a complete list of waypoint weather
    records.
    """

    return [
        normalize_weather(weather)
        for weather in weather_data
    ]