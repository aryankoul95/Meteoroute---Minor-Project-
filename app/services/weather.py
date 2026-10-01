import httpx
import asyncio

async def fetch_point_weather(client: httpx.AsyncClient, waypt: dict) -> dict:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={waypt['lat']}&longitude={waypt['lon']}&current_weather=true&hourly=precipitation"
    try:
        res = await client.get(url, timeout=5.0)
        res.raise_for_status()
        data = res.json()
        current = data.get('current_weather', {})
        
        # Get hourly precipitation if available, else 0.0
        precip = data.get('hourly', {}).get('precipitation', [0.0])[0]

        return {
            "latitude": waypt["lat"],
            "longitude": waypt["lon"],
            "distance_from_start_km": waypt["dist_km"],
            "estimated_arrival_minutes": waypt["eta_min"],
            "temperature_c": current.get('temperature', 0.0),
            "wind_speed_kmh": current.get('windspeed', 0.0),
            "precipitation_mm": precip,
            "weather_code": current.get('weathercode', 0)
        }
    except Exception as e:
        return {
            "latitude": waypt["lat"],
            "longitude": waypt["lon"],
            "distance_from_start_km": waypt["dist_km"],
            "estimated_arrival_minutes": waypt["eta_min"],
            "temperature_c": 0.0,
            "wind_speed_kmh": 0.0,
            "precipitation_mm": 0.0,
            "weather_code": -1
        }

async def batch_fetch_weather(waypoints: list) -> list:
    async with httpx.AsyncClient() as client:
        tasks = [fetch_point_weather(client, pt) for pt in waypoints]
        results = await asyncio.gather(*tasks)
    return results