from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def calculate_cap_risk(cap_alerts: list[dict]) -> dict:
    cap_score = 0.0
    cap_hazards = []

    for alert in cap_alerts:

        for info in alert.get("info", []):

            event = info.get("event") or "CAP Hazard"

            severity = (
                info.get("severity") or ""
            ).lower()

            urgency = (
                info.get("urgency") or ""
            ).lower()

            certainty = (
                info.get("certainty") or ""
            ).lower()

            # Severity contribution
            if severity == "extreme":
                cap_score += 40.0

            elif severity == "severe":
                cap_score += 30.0

            elif severity == "moderate":
                cap_score += 15.0

            # Urgency contribution
            if urgency == "immediate":
                cap_score += 15.0

            elif urgency == "expected":
                cap_score += 5.0

            # Certainty contribution
            if certainty == "observed":
                cap_score += 10.0

            elif certainty == "likely":
                cap_score += 5.0

            hazard_text = f"CAP Alert: {event}"

            if hazard_text not in cap_hazards:
                cap_hazards.append(hazard_text)

    return {
        "cap_score": min(cap_score, 75.0),
        "cap_hazards": cap_hazards,
    }


def calculate_segment_risk(
    precipitation_mm: float | None,
    wind_speed_kmh: float | None,
    temp_c: float | None,
    weather_code: int | None,
    cap_alerts: list[dict] | None = None,
) -> dict:

    # Safely handle missing weather values
    precipitation_mm = _safe_float(
        precipitation_mm
    )

    wind_speed_kmh = _safe_float(
        wind_speed_kmh
    )

    temp_c = _safe_float(
        temp_c
    )

    weather_code = _safe_int(
        weather_code
    )

    risk_score = 0.0
    hazard_reasons = []

    # -------------------------------------------------
    # Rainfall risk
    # -------------------------------------------------

    if precipitation_mm > 50.0:

        risk_score += 40.0

        hazard_reasons.append(
            "Extreme Rainfall / Flood Risk"
        )

    elif precipitation_mm > 15.0:

        risk_score += 25.0

        hazard_reasons.append(
            "Heavy Rainfall"
        )

    elif precipitation_mm > 5.0:

        risk_score += 10.0

        hazard_reasons.append(
            "Moderate Rain"
        )

    # -------------------------------------------------
    # Wind risk
    # -------------------------------------------------

    if wind_speed_kmh > 60.0:

        risk_score += 35.0

        hazard_reasons.append(
            "Severe High Winds"
        )

    elif wind_speed_kmh > 35.0:

        risk_score += 15.0

        hazard_reasons.append(
            "Strong Winds"
        )

    # -------------------------------------------------
    # Weather-code hazards
    # -------------------------------------------------

    if weather_code in [45, 48]:

        risk_score += 25.0

        hazard_reasons.append(
            "Dense Fog / Low Visibility"
        )

    elif weather_code in [95, 96, 99]:

        risk_score += 35.0

        hazard_reasons.append(
            "Active Thunderstorm Hazard"
        )

    # -------------------------------------------------
    # CAP alert risk
    # -------------------------------------------------

    cap_result = calculate_cap_risk(
        cap_alerts or []
    )

    risk_score += cap_result["cap_score"]

    hazard_reasons.extend(
        cap_result["cap_hazards"]
    )

    # -------------------------------------------------
    # Final risk score
    # -------------------------------------------------

    final_score = min(
        round(risk_score, 1),
        100.0,
    )

    if final_score >= 60.0:

        category = "HIGH"

    elif final_score >= 25.0:

        category = "MEDIUM"

    else:

        category = "LOW"

    # -------------------------------------------------
    # Default hazard message
    # -------------------------------------------------

    if not hazard_reasons:

        hazard_reasons.append(
            "Clear / Safe Driving Conditions"
        )

    return {
        "risk_score": final_score,
        "risk_category": category,
        "hazards": hazard_reasons,
    }


def evaluate_route_risk(
    waypoints_weather: list[dict],
) -> dict:

    total_score = 0.0

    high_risk_segments = 0

    evaluated_waypoints = []

    for pt in waypoints_weather:

        risk_info = calculate_segment_risk(

            precipitation_mm=pt.get(
                "precipitation_mm"
            ),

            wind_speed_kmh=pt.get(
                "wind_speed_kmh"
            ),

            temp_c=pt.get(
                "temperature_c"
            ),

            weather_code=pt.get(
                "weather_code"
            ),

            cap_alerts=pt.get(
                "cap_alerts",
                [],
            ),
        )

        if (
            risk_info["risk_category"]
            == "HIGH"
        ):

            high_risk_segments += 1

        total_score += (
            risk_info["risk_score"]
        )

        evaluated_waypoints.append(
            {
                **pt,
                **risk_info,
            }
        )

    # -------------------------------------------------
    # Overall route risk
    # -------------------------------------------------

    if waypoints_weather:

        avg_route_risk = round(
            total_score
            / len(waypoints_weather),
            1,
        )

    else:

        avg_route_risk = 0.0

    # -------------------------------------------------
    # Route safety status
    # -------------------------------------------------

    if (
        avg_route_risk > 50.0
        or high_risk_segments >= 2
    ):

        route_safety_status = "UNSAFE"

    else:

        route_safety_status = "SAFE"

    return {
        "overall_route_risk_score": (
            avg_route_risk
        ),

        "high_risk_segments_count": (
            high_risk_segments
        ),

        "route_safety_status": (
            route_safety_status
        ),

        "waypoints": evaluated_waypoints,
    }