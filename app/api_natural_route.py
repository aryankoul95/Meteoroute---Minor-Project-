from fastapi import APIRouter, HTTPException

from app.schemas.intent import IntentRequest

from app.services.intent_extractor import (
    extract_travel_intent_llm,
)

from app.services.geocoding import geocode_place

from app.services.routing import (
    get_osrm_route,
    sample_waypoints,
    build_route_segments,
)

from app.services.weather import (
    batch_fetch_weather,
)

from app.services.weather_normalizer import (
    normalize_weather_batch,
)

from app.services.cap_client import (
    fetch_official_cap_alerts,
)

from app.services.cap_parser import (
    parse_cap_alert,
)

from app.services.cap_normalizer import (
    normalize_cap_alert,
)

from app.services.cap_matcher import (
    match_alerts_to_waypoints,
)

from app.services.risk_engine import (
    evaluate_route_risk,
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
        # STEP 7: Fetch real weather
        # -------------------------------------------------

        weather_data = await batch_fetch_weather(
            sampled_points,
            intent.departure_time,
        )

        # -------------------------------------------------
        # STEP 8: Normalize weather
        # -------------------------------------------------

        normalized_weather = normalize_weather_batch(
            weather_data
        )

        # -------------------------------------------------
        # STEP 9: Fetch official IMD CAP alerts
        # -------------------------------------------------

        cap_xml_alerts = await fetch_official_cap_alerts()

        cap_alerts = []

        for xml_content in cap_xml_alerts:
            try:
                parsed_alert = parse_cap_alert(
                    xml_content
                )

                normalized_alert = normalize_cap_alert(
                    parsed_alert
                )

                cap_alerts.append(
                    normalized_alert
                )

            except Exception:
                continue

        # -------------------------------------------------
        # STEP 10: Prepare route waypoints
        # for CAP matching
        # -------------------------------------------------

        route_waypoints = []

        for weather in normalized_weather:
            route_waypoints.append(
                {
                    "latitude": weather["latitude"],
                    "longitude": weather["longitude"],
                    "distance_from_start_km": (
                        weather[
                            "distance_from_start_km"
                        ]
                    ),
                    "estimated_arrival_minutes": (
                        weather[
                            "estimated_arrival_minutes"
                        ]
                    ),
                }
            )

        # -------------------------------------------------
        # STEP 11: Match CAP alerts
        # -------------------------------------------------

        matched_waypoints = (
            match_alerts_to_waypoints(
                route_waypoints,
                cap_alerts,
                intent.departure_time,
            )
        )

        # -------------------------------------------------
        # STEP 12: Combine weather + CAP
        # -------------------------------------------------

        combined_waypoints = []

        for weather, matched in zip(
            normalized_weather,
            matched_waypoints,
        ):
            combined_waypoints.append(
                {
                    "latitude": weather["latitude"],
                    "longitude": weather["longitude"],
                    "distance_from_start_km": (
                        weather[
                            "distance_from_start_km"
                        ]
                    ),
                    "estimated_arrival_minutes": (
                        weather[
                            "estimated_arrival_minutes"
                        ]
                    ),
                    "forecast_time": (
                        weather["forecast_time"]
                    ),
                    "temperature_c": (
                        weather["temperature_c"]
                    ),
                    "wind_speed_kmh": (
                        weather["wind_speed_kmh"]
                    ),
                    "wind_gust_kmh": (
                        weather["wind_gust_kmh"]
                    ),
                    "precipitation_mm": (
                        weather["precipitation_mm"]
                    ),
                    "weather_code": (
                        weather["weather_code"]
                    ),
                    "weather_source": (
                        weather["source"]
                    ),
                    "cap_alerts": (
                        matched["cap_alerts"]
                    ),
                }
            )

        # -------------------------------------------------
        # STEP 13: Evaluate combined route risk
        # -------------------------------------------------

        risk_result = evaluate_route_risk(
            combined_waypoints
        )

        # -------------------------------------------------
        # STEP 14: Count CAP-matched waypoints
        # -------------------------------------------------

        cap_matched_count = sum(
            1
            for waypoint in combined_waypoints
            if waypoint["cap_alerts"]
        )

        # -------------------------------------------------
        # STEP 15: Build route segments
        # -------------------------------------------------

        segments = build_route_segments(
            risk_result["waypoints"]
        )

        # -------------------------------------------------
        # STEP 16: Attach risk information to segments
        #
        # Segment risk = maximum risk of its
        # start/end waypoints.
        # -------------------------------------------------

        for segment in segments:

            start_index = (
                segment["segment_id"] - 1
            )

            end_index = (
                segment["segment_id"]
            )

            start_waypoint = risk_result[
                "waypoints"
            ][start_index]

            end_waypoint = risk_result[
                "waypoints"
            ][end_index]

            start_score = float(
                start_waypoint.get(
                    "risk_score",
                    0.0,
                )
            )

            end_score = float(
                end_waypoint.get(
                    "risk_score",
                    0.0,
                )
            )

            if start_score >= end_score:
                segment_score = start_score
                segment_category = (
                    start_waypoint.get(
                        "risk_category",
                        "LOW",
                    )
                )
            else:
                segment_score = end_score
                segment_category = (
                    end_waypoint.get(
                        "risk_category",
                        "LOW",
                    )
                )

            hazards = []

            for waypoint in (
                start_waypoint,
                end_waypoint,
            ):
                for hazard in waypoint.get(
                    "hazards",
                    [],
                ):
                    if hazard not in hazards:
                        hazards.append(hazard)

            segment["risk_score"] = round(
                segment_score,
                1,
            )

            segment["risk_category"] = (
                segment_category
            )

            segment["hazards"] = hazards

        # -------------------------------------------------
        # STEP 17: Return final route response
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
                risk_result["waypoints"]
            ),

            "total_segments": len(
                segments
            ),

            "cap_alerts_fetched": len(
                cap_alerts
            ),

            "cap_matched_waypoints": (
                cap_matched_count
            ),

            "overall_route_risk_score": (
                risk_result[
                    "overall_route_risk_score"
                ]
            ),

            "high_risk_segments_count": (
                risk_result[
                    "high_risk_segments_count"
                ]
            ),

            "route_safety_status": (
                risk_result[
                    "route_safety_status"
                ]
            ),

            "waypoints": (
                risk_result["waypoints"]
            ),

            "segments": segments,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )