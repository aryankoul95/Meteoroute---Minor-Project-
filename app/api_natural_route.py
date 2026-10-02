from fastapi import APIRouter, HTTPException

from app.schemas.intent import IntentRequest
from app.services.intent_extractor import (
    extract_travel_intent_llm,
)
from app.services.geocoding import geocode_place
from app.services.routing import (
    get_osrm_route,
    sample_waypoints,
)

router = APIRouter()


@router.post("/natural-route")
async def natural_route(payload: IntentRequest):

    try:
        # -------------------------------------------------
        # STEP 1: Extract travel intent using Gemini
        # -------------------------------------------------

        intent = await extract_travel_intent_llm(
            payload.query
        )

        # -------------------------------------------------
        # STEP 2: Validate intent
        # -------------------------------------------------

        if intent.intent != "route_planning":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Query is not a "
                    "route-planning request."
                ),
            )

        if (
            not intent.origin
            or not intent.destination
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract origin "
                    "and destination."
                ),
            )

        # -------------------------------------------------
        # STEP 3: Geocode origin
        # -------------------------------------------------

        origin = geocode_place(
            f"{intent.origin}, India"
        )

        if origin is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Could not geocode origin: "
                    f"{intent.origin}"
                ),
            )

        # -------------------------------------------------
        # STEP 4: Geocode destination
        # -------------------------------------------------

        destination = geocode_place(
            f"{intent.destination}, India"
        )

        if destination is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Could not geocode destination: "
                    f"{intent.destination}"
                ),
            )

        # -------------------------------------------------
        # STEP 5: Get OSRM route
        # -------------------------------------------------

        geometry, distance_km, duration_hrs = (
            await get_osrm_route(
                origin["latitude"],
                origin["longitude"],
                destination["latitude"],
                destination["longitude"],
            )
        )

        # -------------------------------------------------
        # STEP 6: Sample route waypoints
        # -------------------------------------------------

        sampled_points = sample_waypoints(
            geometry,
            15.0,
            duration_hrs,
            distance_km,
        )

        # -------------------------------------------------
        # STEP 7: Prepare map-ready waypoints
        #
        # Weather and risk values are placeholders for
        # now. Week 3 will replace these with real
        # weather/CAP data.
        # -------------------------------------------------

        waypoints = []

        for point in sampled_points:

            waypoints.append(
                {
                    "latitude": point["lat"],
                    "longitude": point["lon"],
                    "distance_from_start_km": (
                        point["dist_km"]
                    ),
                    "estimated_arrival_minutes": (
                        point["eta_min"]
                    ),

                    # Placeholder values.
                    # These will be replaced in Week 3.
                    "temperature_c": 25.0,
                    "wind_speed_kmh": 12.0,
                    "precipitation_mm": 0.0,

                    "risk_score": 10.0,
                    "risk_category": "LOW",
                    "hazards": [],
                }
            )

        # -------------------------------------------------
        # STEP 8: Return complete route response
        # -------------------------------------------------

        return {
            "intent": intent.model_dump(),

            "origin_coordinates": origin,

            "destination_coordinates": destination,

            "total_distance_km": round(
                distance_km,
                2,
            ),

            "total_duration_hours": round(
                duration_hrs,
                2,
            ),

            "total_waypoints_sampled": len(
                waypoints
            ),

            "overall_route_risk_score": 10.0,

            "high_risk_segments_count": 0,

            "route_safety_status": "SAFE",

            "waypoints": waypoints,
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )