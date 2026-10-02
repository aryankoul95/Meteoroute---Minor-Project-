from fastapi import APIRouter, HTTPException

from app.schemas.intent import IntentRequest
from app.services.intent_extractor import extract_travel_intent
from app.services.geocoding import geocode_place
from app.services.routing import get_osrm_route

router = APIRouter()


@router.post("/natural-route")
async def natural_route(payload: IntentRequest):
    try:
        intent = extract_travel_intent(payload.query)

        if intent.intent != "route_planning":
            raise HTTPException(
                status_code=400,
                detail="Query is not a route-planning request."
            )

        if not intent.origin or not intent.destination:
            raise HTTPException(
                status_code=400,
                detail="Could not extract origin and destination."
            )

        origin = geocode_place(f"{intent.origin}, India")
        destination = geocode_place(f"{intent.destination}, India")

        if origin is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode origin: {intent.origin}"
            )

        if destination is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode destination: {intent.destination}"
            )

        geometry, distance_km, duration_hrs = await get_osrm_route(
            origin["latitude"],
            origin["longitude"],
            destination["latitude"],
            destination["longitude"],
        )

        return {
            "intent": intent.model_dump(),
            "origin_coordinates": origin,
            "destination_coordinates": destination,
            "total_distance_km": round(distance_km, 2),
            "total_duration_hours": round(duration_hrs, 2),
            "geometry": geometry,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
