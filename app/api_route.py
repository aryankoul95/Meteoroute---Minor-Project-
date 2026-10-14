
from fastapi import APIRouter, HTTPException
from app.schemas.route import RouteRequest, RouteResponse, WaypointWeatherRisk
from app.services.routing import get_osrm_route, sample_waypoints

router = APIRouter()


@router.post("/route-pipeline", response_model=RouteResponse)
async def compute_route_pipeline(payload: RouteRequest):
    try:
        # 1. Fetch route geometry from OSRM
        geometry, total_dist_km, total_duration_hrs = await get_osrm_route(
            payload.start_lat,
            payload.start_lon,
            payload.end_lat,
            payload.end_lon,
        )

        # 2. Sample waypoints along the route
        interval = payload.sampling_interval_km or 15.0
        sampled_pts = sample_waypoints(
            geometry,
            interval,
            total_duration_hrs,
            total_dist_km,
        )

        # 3. Format sampled waypoints for response
        waypoints_data = []
        for pt in sampled_pts:
            waypoints_data.append(
                WaypointWeatherRisk(
                    latitude=pt["lat"],
                    longitude=pt["lon"],
                    distance_from_start_km=pt["dist_km"],
                    estimated_arrival_minutes=pt["eta_min"],
                    temperature_c=25.0,
                    wind_speed_kmh=12.0,
                    precipitation_mm=0.0,
                    weather_code=0,
                    risk_score=10.0,
                    risk_category="Low",
                    hazards=[],
                )
            )

        # 4. Build segments between consecutive waypoints
        segments = []
        for i in range(len(waypoints_data) - 1):
            start = waypoints_data[i]
            end = waypoints_data[i + 1]

            segments.append(
                {
                    "segment_id": i + 1,
                    "start_lat": start.latitude,
                    "start_lon": start.longitude,
                    "end_lat": end.latitude,
                    "end_lon": end.longitude,
                    "distance_km": round(
                        end.distance_from_start_km
                        - start.distance_from_start_km,
                        2,
                    ),
                    "start_eta_minutes": start.estimated_arrival_minutes,
                    "end_eta_minutes": end.estimated_arrival_minutes,
                    "risk_score": max(
                        start.risk_score,
                        end.risk_score,
                    ),
                    "risk_category": (
                        start.risk_category
                        if start.risk_score >= end.risk_score
                        else end.risk_category
                    ),
                    "hazards": list(
                        dict.fromkeys(start.hazards + end.hazards)
                    ),
                }
            )

        # 5. Return route summary, waypoints, and segments
        return RouteResponse(
            total_distance_km=round(total_dist_km, 2),
            total_duration_hours=round(total_duration_hrs, 2),
            total_waypoints_sampled=len(waypoints_data),
            total_segments=len(segments),
            overall_route_risk_score=10.0,
            high_risk_segments_count=0,
            route_safety_status="Safe",
            waypoints=waypoints_data,
            segments=segments,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
