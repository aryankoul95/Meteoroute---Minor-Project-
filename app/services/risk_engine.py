def calculate_segment_risk(precipitation_mm: float, wind_speed_kmh: float, temp_c: float, weather_code: int) -> dict:
    risk_score = 0.0
    hazard_reasons = []

    # Precipitation Risk Rules
    if precipitation_mm > 50.0:
        risk_score += 40.0
        hazard_reasons.append("Extreme Rainfall / Flood Risk")
    elif precipitation_mm > 15.0:
        risk_score += 25.0
        hazard_reasons.append("Heavy Rainfall")
    elif precipitation_mm > 5.0:
        risk_score += 10.0
        hazard_reasons.append("Moderate Rain")

    # Wind Risk Rules
    if wind_speed_kmh > 60.0:
        risk_score += 35.0
        hazard_reasons.append("Severe High Winds")
    elif wind_speed_kmh > 35.0:
        risk_score += 15.0
        hazard_reasons.append("Strong Gusts")

    # WMO Weather Code Checks (Fog, Thunderstorm, Snow)
    if weather_code in [45, 48]:
        risk_score += 25.0
        hazard_reasons.append("Dense Fog / Low Visibility")
    elif weather_code in [95, 96, 99]:
        risk_score += 35.0
        hazard_reasons.append("Active Thunderstorm Hazard")

    final_score = min(round(risk_score, 1), 100.0)

    if final_score >= 60.0:
        category = "HIGH"
    elif final_score >= 25.0:
        category = "MEDIUM"
    else:
        category = "LOW"

    return {
        "risk_score": final_score,
        "risk_category": category,
        "hazards": hazard_reasons if hazard_reasons else ["Clear / Safe Driving Conditions"]
    }

def evaluate_route_risk(waypoints_weather: list) -> dict:
    total_score = 0.0
    high_risk_segments = 0
    evaluated_waypoints = []

    for pt in waypoints_weather:
        risk_info = calculate_segment_risk(
            precipitation_mm=pt.get("precipitation_mm", 0.0),
            wind_speed_kmh=pt.get("wind_speed_kmh", 0.0),
            temp_c=pt.get("temperature_c", 0.0),
            weather_code=pt.get("weather_code", 0)
        )

        if risk_info["risk_category"] == "HIGH":
            high_risk_segments += 1

        total_score += risk_info["risk_score"]
        evaluated_waypoints.append({**pt, **risk_info})

    avg_route_risk = round(total_score / len(waypoints_weather), 1) if waypoints_weather else 0.0

    return {
        "overall_route_risk_score": avg_route_risk,
        "high_risk_segments_count": high_risk_segments,
        "route_safety_status": "UNSAFE" if avg_route_risk > 50.0 or high_risk_segments >= 2 else "SAFE",
        "waypoints": evaluated_waypoints
    }