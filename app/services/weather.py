import asyncio
from datetime import datetime, timedelta, timezone

import httpx


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# India Standard Time = UTC + 5:30
IST = timezone(timedelta(hours=5, minutes=30))


def _parse_departure_time(
    departure_time: str | None,
) -> datetime:

    if departure_time:

        try:
            parsed = datetime.fromisoformat(
                departure_time
            )

            # Gemini returns a timezone-naive time.
            # Treat it as Indian Standard Time.
            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=IST
                )

            return parsed

        except ValueError:
            pass

    # Fallback if no departure time is provided.
    return datetime.now(IST)


def _select_forecast_index(
    hourly_times: list[str],
    estimated_arrival_minutes: float,
    departure_time: str | None,
) -> int:

    if not hourly_times:
        return 0

    departure = _parse_departure_time(
        departure_time
    )

    arrival_time = (
        departure
        + timedelta(
            minutes=estimated_arrival_minutes
        )
    )

    # Open-Meteo is requested in UTC.
    arrival_time_utc = arrival_time.astimezone(
        timezone.utc
    )

    best_index = 0
    best_difference = None

    for index, time_string in enumerate(
        hourly_times
    ):

        try:

            forecast_time = datetime.fromisoformat(
                time_string
            )

            if forecast_time.tzinfo is None:
                forecast_time = forecast_time.replace(
                    tzinfo=timezone.utc
                )

            difference = abs(
                (
                    forecast_time
                    - arrival_time_utc
                ).total_seconds()
            )

            if (
                best_difference is None
                or difference < best_difference
            ):

                best_difference = difference
                best_index = index

        except ValueError:
            continue

    return best_index


async def fetch_point_weather(
    client: httpx.AsyncClient,
    waypt: dict,
    departure_time: str | None = None,
) -> dict:

    latitude = waypt["lat"]
    longitude = waypt["lon"]

    estimated_arrival_minutes = waypt.get(
        "eta_min",
        0.0,
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_gusts_10m"
        ),
        "forecast_days": 2,
        "timezone": "UTC",
    }

    last_error = None

    for attempt in range(3):

        try:

            response = await client.get(
                OPEN_METEO_URL,
                params=params,
                timeout=15.0,
            )

            response.raise_for_status()

            data = response.json()

            hourly = data.get(
                "hourly",
                {},
            )

            times = hourly.get(
                "time",
                [],
            )

            index = _select_forecast_index(
                times,
                estimated_arrival_minutes,
                departure_time,
            )

            temperatures = hourly.get(
                "temperature_2m",
                [],
            )

            precipitation = hourly.get(
                "precipitation",
                [],
            )

            weather_codes = hourly.get(
                "weather_code",
                [],
            )

            wind_speeds = hourly.get(
                "wind_speed_10m",
                [],
            )

            wind_gusts = hourly.get(
                "wind_gusts_10m",
                [],
            )

            return {
                "latitude": latitude,
                "longitude": longitude,

                "distance_from_start_km": (
                    waypt.get(
                        "dist_km",
                        0.0,
                    )
                ),

                "estimated_arrival_minutes": (
                    estimated_arrival_minutes
                ),

                "forecast_time": (
                    times[index]
                    if index < len(times)
                    else None
                ),

                "temperature_c": (
                    temperatures[index]
                    if index < len(temperatures)
                    else None
                ),

                "wind_speed_kmh": (
                    wind_speeds[index]
                    if index < len(wind_speeds)
                    else None
                ),

                "wind_gust_kmh": (
                    wind_gusts[index]
                    if index < len(wind_gusts)
                    else None
                ),

                "precipitation_mm": (
                    precipitation[index]
                    if index < len(precipitation)
                    else None
                ),

                "weather_code": (
                    weather_codes[index]
                    if index < len(weather_codes)
                    else None
                ),

                "weather_source": "Open-Meteo",
            }

        except Exception as e:

            last_error = repr(e)

            if attempt < 2:

                await asyncio.sleep(
                    1.0 * (attempt + 1)
                )

    return {
        "latitude": latitude,
        "longitude": longitude,

        "distance_from_start_km": (
            waypt.get(
                "dist_km",
                0.0,
            )
        ),

        "estimated_arrival_minutes": (
            estimated_arrival_minutes
        ),

        "forecast_time": None,

        "temperature_c": None,
        "wind_speed_kmh": None,
        "wind_gust_kmh": None,
        "precipitation_mm": None,
        "weather_code": None,

        "weather_source": "Open-Meteo",
        "weather_error": last_error,
    }


async def batch_fetch_weather(
    waypoints: list,
    departure_time: str | None = None,
) -> list:

    semaphore = asyncio.Semaphore(8)

    async def fetch_with_limit(
        client: httpx.AsyncClient,
        waypoint: dict,
    ):

        async with semaphore:

            return await fetch_point_weather(
                client,
                waypoint,
                departure_time,
            )

    async with httpx.AsyncClient() as client:

        tasks = [
            fetch_with_limit(
                client,
                waypoint,
            )
            for waypoint in waypoints
        ]

        results = await asyncio.gather(
            *tasks
        )

    return results