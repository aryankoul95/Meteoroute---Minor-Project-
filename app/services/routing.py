import httpx
import os
from geopy.distance import geodesic


async def get_osrm_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
):
    base_url = os.getenv("OSRM_URL", "http://localhost:5000")

    url = (
        f"{base_url}/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full&geometries=geojson"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    route = data["routes"][0]

    geometry = route["geometry"]["coordinates"]
    distance_km = route["distance"] / 1000.0
    duration_hrs = route["duration"] / 3600.0

    return geometry, distance_km, duration_hrs


def sample_waypoints(
    geometry: list,
    target_interval_km: float,
    total_duration_hrs: float,
    total_distance_km: float,
):
    sampled = []
    accumulated_dist = 0.0
    last_sampled_dist = 0.0

    # Average speed in km/h to estimate ETA at each waypoint
    avg_speed_kmh = (
        total_distance_km / total_duration_hrs
        if total_duration_hrs > 0
        else 60.0
    )

    # Add starting point
    first_pt = geometry[0]

    sampled.append({
        "lat": first_pt[1],
        "lon": first_pt[0],
        "dist_km": 0.0,
        "eta_min": 0.0,
    })

    for i in range(1, len(geometry)):
        prev_pt = (
            geometry[i - 1][1],
            geometry[i - 1][0],
        )

        curr_pt = (
            geometry[i][1],
            geometry[i][0],
        )

        segment_dist = geodesic(
            prev_pt,
            curr_pt,
        ).km

        accumulated_dist += segment_dist

        if (
            accumulated_dist - last_sampled_dist
            >= target_interval_km
        ):
            eta_minutes = (
                accumulated_dist / avg_speed_kmh
            ) * 60.0

            sampled.append({
                "lat": curr_pt[0],
                "lon": curr_pt[1],
                "dist_km": round(
                    accumulated_dist,
                    2,
                ),
                "eta_min": round(
                    eta_minutes,
                    1,
                ),
            })

            last_sampled_dist = accumulated_dist

    # Always add destination point if not already added
    last_pt = geometry[-1]

    if not (
        sampled[-1]["lat"] == last_pt[1]
        and sampled[-1]["lon"] == last_pt[0]
    ):
        sampled.append({
            "lat": last_pt[1],
            "lon": last_pt[0],
            "dist_km": round(
                total_distance_km,
                2,
            ),
            "eta_min": round(
                total_duration_hrs * 60.0,
                1,
            ),
        })

    return sampled


def build_route_segments(
    waypoints: list,
) -> list:
    segments = []

    for i in range(len(waypoints) - 1):
        start = waypoints[i]
        end = waypoints[i + 1]

        # Support both waypoint formats:
        # lat/lon and latitude/longitude
        start_lat = start.get(
            "latitude",
            start.get("lat"),
        )
        start_lon = start.get(
            "longitude",
            start.get("lon"),
        )

        end_lat = end.get(
            "latitude",
            end.get("lat"),
        )
        end_lon = end.get(
            "longitude",
            end.get("lon"),
        )

        start_distance = start.get(
            "distance_from_start_km",
            start.get("dist_km", 0.0),
        )

        end_distance = end.get(
            "distance_from_start_km",
            end.get("dist_km", 0.0),
        )

        start_eta = start.get(
            "estimated_arrival_minutes",
            start.get("eta_min", 0.0),
        )

        end_eta = end.get(
            "estimated_arrival_minutes",
            end.get("eta_min", 0.0),
        )

        segments.append({
            "segment_id": i + 1,

            "start": {
                "lat": start_lat,
                "lon": start_lon,
            },

            "end": {
                "lat": end_lat,
                "lon": end_lon,
            },

            "start_distance_km": start_distance,

            "end_distance_km": end_distance,

            "distance_km": round(
                end_distance - start_distance,
                2,
            ),

            "start_eta_min": start_eta,

            "end_eta_min": end_eta,
        })

    return segments