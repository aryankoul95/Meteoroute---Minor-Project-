from fastapi import APIRouter, HTTPException

from app.schemas.intent import IntentRequest
from app.services.intent_extractor import extract_travel_intent
from app.services.geocoding import geocode_place
from app.services.routing import get_osrm_route, sample_waypoints

router = APIRouter()


@router.post("/natural-route")
async def natural_route(payload: IntentRequest):
    try:
        intent = extract_travel_intent(payload.query)

        if intent.intent != "route_planning":
            raise HTTPException(
                status_code=400,
                detail="Query is not a route-planning request.",
            )

        if not intent.origin or not intent.destination:
            raise HTTPException(
                status_code=400,
                detail="Could not extract origin and destination.",
            )

        origin = geocode_place(f"{intent.origin}, India")
        destination = geocode_place(f"{intent.destination}, India")

        if origin is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode origin: {intent.origin}",
            )

        if destination is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode destination: {intent.destination}",
            )

        geometry, distance_km, duration_hrs = await get_osrm_route(
            origin["latitude"],
            origin["longitude"],
            destination["latitude"],
            destination["longitude"],
        )

        sampled_points = sample_waypoints(
            geometry,
            15.0,
            duration_hrs,
            distance_km,
        )

        waypoints = []

        for point in sampled_points:
            waypoints.append(
                {
                    "latitude": point["lat"],
                    "longitude": point["lon"],
                    "distance_from_start_km": point["dist_km"],
                    "estimated_arrival_minutes": point["eta_min"],
                    "temperature_c": 25.0,
                    "wind_speed_kmh": 12.0,
                    "precipitation_mm": 0.0,
                    "risk_score": 10.0,
                    "risk_category": "LOW",
                    "hazards": [],
                }
            )

        return {
            "intent": intent.model_dump(),
            "origin_coordinates": origin,
            "destination_coordinates": destination,
            "total_distance_km": round(distance_km, 2),
            "total_duration_hours": round(duration_hrs, 2),
            "total_waypoints_sampled": len(waypoints),
            "overall_route_risk_score": 10.0,
            "high_risk_segments_count": 0,
            "route_safety_status": "SAFE",
            "waypoints": waypoints,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))