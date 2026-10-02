from typing import Any


# ============================================================
# CONFIGURABLE RISK-SCORING RULES
# ============================================================

RISK_RULES = {
    "rainfall": {
        "extreme": {
            "threshold_mm": 50.0,
            "score": 40.0,
            "hazard": "Extreme Rainfall / Flood Risk",
        },
        "heavy": {
            "threshold_mm": 15.0,
            "score": 25.0,
            "hazard": "Heavy Rainfall",
        },
        "moderate": {
            "threshold_mm": 5.0,
            "score": 10.0,
            "hazard": "Moderate Rain",
        },
    },

    "wind": {
        "severe": {
            "threshold_kmh": 60.0,
            "score": 35.0,
            "hazard": "Severe High Winds",
        },
        "strong": {
            "threshold_kmh": 35.0,
            "score": 15.0,
            "hazard": "Strong Winds",
        },
    },

    "weather_codes": {
        "fog": {
            "codes": [45, 48],
            "score": 25.0,
            "hazard": "Dense Fog / Low Visibility",
        },
        "thunderstorm": {
            "codes": [95, 96, 99],
            "score": 35.0,
            "hazard": "Active Thunderstorm Hazard",
        },
    },

    "risk_categories": {
        "high_threshold": 60.0,
        "medium_threshold": 25.0,
    },

    "route_safety": {
        "average_risk_threshold": 50.0,
        "high_risk_segment_limit": 2,
    },
}


# ============================================================
# SAFE VALUE CONVERSION
# ============================================================

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


# ============================================================
# FORECAST-DERIVED RISK
# ============================================================

def calculate_forecast_risk(
    precipitation_mm: float | None,
    wind_speed_kmh: float | None,
    temp_c: float | None,
    weather_code: int | None,
) -> dict:

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

    forecast_score = 0.0
    forecast_hazards = []

    # --------------------------------------------------------
    # Rainfall
    # --------------------------------------------------------

    rainfall_rules = RISK_RULES["rainfall"]

    if (
        precipitation_mm
        > rainfall_rules["extreme"]["threshold_mm"]
    ):
        forecast_score += rainfall_rules["extreme"]["score"]

        forecast_hazards.append(
            rainfall_rules["extreme"]["hazard"]
        )

    elif (
        precipitation_mm
        > rainfall_rules["heavy"]["threshold_mm"]
    ):
        forecast_score += rainfall_rules["heavy"]["score"]

        forecast_hazards.append(
            rainfall_rules["heavy"]["hazard"]
        )

    elif (
        precipitation_mm
        > rainfall_rules["moderate"]["threshold_mm"]
    ):
        forecast_score += rainfall_rules["moderate"]["score"]

        forecast_hazards.append(
            rainfall_rules["moderate"]["hazard"]
        )

    # --------------------------------------------------------
    # Wind
    # --------------------------------------------------------

    wind_rules = RISK_RULES["wind"]

    if (
        wind_speed_kmh
        > wind_rules["severe"]["threshold_kmh"]
    ):
        forecast_score += wind_rules["severe"]["score"]

        forecast_hazards.append(
            wind_rules["severe"]["hazard"]
        )

    elif (
        wind_speed_kmh
        > wind_rules["strong"]["threshold_kmh"]
    ):
        forecast_score += wind_rules["strong"]["score"]

        forecast_hazards.append(
            wind_rules["strong"]["hazard"]
        )

    # --------------------------------------------------------
    # Weather-code hazards
    # --------------------------------------------------------

    weather_rules = RISK_RULES["weather_codes"]

    fog_rule = weather_rules["fog"]

    if weather_code in fog_rule["codes"]:
        forecast_score += fog_rule["score"]

        forecast_hazards.append(
            fog_rule["hazard"]
        )

    thunderstorm_rule = (
        weather_rules["thunderstorm"]
    )

    if weather_code in thunderstorm_rule["codes"]:
        forecast_score += thunderstorm_rule["score"]

        forecast_hazards.append(
            thunderstorm_rule["hazard"]
        )

    return {
        "forecast_risk_score": min(
            round(forecast_score, 1),
            100.0,
        ),
        "forecast_hazards": forecast_hazards,
    }


# ============================================================
# OFFICIAL CAP ALERT RISK
# ============================================================

def calculate_cap_risk(
    cap_alerts: list[dict],
) -> dict:

    cap_score = 0.0
    cap_hazards = []
    cap_metadata = []

    for alert in cap_alerts:

        # ----------------------------------------------------
        # Alert-level metadata
        # ----------------------------------------------------

        alert_metadata = {
            "source": "IMD CAP",
            "identifier": alert.get(
                "identifier"
            ),
            "sender": alert.get(
                "sender"
            ),
            "sent": alert.get(
                "sent"
            ),
            "status": alert.get(
                "status"
            ),
            "message_type": alert.get(
                "message_type"
            ),
            "scope": alert.get(
                "scope"
            ),
        }

        for info in alert.get("info", []):

            event = (
                info.get("event")
                or "CAP Hazard"
            )

            severity = (
                info.get("severity")
                or ""
            ).lower()

            urgency = (
                info.get("urgency")
                or ""
            ).lower()

            certainty = (
                info.get("certainty")
                or ""
            ).lower()

            # ------------------------------------------------
            # Severity contribution
            # ------------------------------------------------

            if severity == "extreme":
                cap_score += 40.0

            elif severity == "severe":
                cap_score += 30.0

            elif severity == "moderate":
                cap_score += 15.0

            # ------------------------------------------------
            # Urgency contribution
            # ------------------------------------------------

            if urgency == "immediate":
                cap_score += 15.0

            elif urgency == "expected":
                cap_score += 5.0

            # ------------------------------------------------
            # Certainty contribution
            # ------------------------------------------------

            if certainty == "observed":
                cap_score += 10.0

            elif certainty == "likely":
                cap_score += 5.0

            hazard_text = (
                f"CAP Alert: {event}"
            )

            if hazard_text not in cap_hazards:
                cap_hazards.append(
                    hazard_text
                )

            # ------------------------------------------------
            # Information-level metadata
            # ------------------------------------------------

            info_metadata = {
                **alert_metadata,
                "event": event,
                "category": info.get(
                    "category"
                ),
                "severity": info.get(
                    "severity"
                ),
                "urgency": info.get(
                    "urgency"
                ),
                "certainty": info.get(
                    "certainty"
                ),
                "effective": info.get(
                    "effective"
                ),
                "onset": info.get(
                    "onset"
                ),
                "expires": info.get(
                    "expires"
                ),
                "headline": info.get(
                    "headline"
                ),
            }

            cap_metadata.append(
                info_metadata
            )

    return {
        "official_alert_risk_score": min(
            round(cap_score, 1),
            75.0,
        ),
        "official_alert_hazards": (
            cap_hazards
        ),
        "official_alert_metadata": (
            cap_metadata
        ),
    }


# ============================================================
# COMBINED SEGMENT RISK
# ============================================================

def calculate_segment_risk(
    precipitation_mm: float | None,
    wind_speed_kmh: float | None,
    temp_c: float | None,
    weather_code: int | None,
    cap_alerts: list[dict] | None = None,
    forecast_time: str | None = None,
    weather_source: str | None = None,
) -> dict:

    # --------------------------------------------------------
    # Forecast-derived risk
    # --------------------------------------------------------

    forecast_result = calculate_forecast_risk(
        precipitation_mm=precipitation_mm,
        wind_speed_kmh=wind_speed_kmh,
        temp_c=temp_c,
        weather_code=weather_code,
    )

    forecast_score = (
        forecast_result[
            "forecast_risk_score"
        ]
    )

    forecast_hazards = (
        forecast_result[
            "forecast_hazards"
        ]
    )

    # --------------------------------------------------------
    # Official CAP alert risk
    # --------------------------------------------------------

    cap_result = calculate_cap_risk(
        cap_alerts or []
    )

    official_alert_score = (
        cap_result[
            "official_alert_risk_score"
        ]
    )

    official_alert_hazards = (
        cap_result[
            "official_alert_hazards"
        ]
    )

    official_alert_metadata = (
        cap_result[
            "official_alert_metadata"
        ]
    )

    # --------------------------------------------------------
    # Total risk
    # --------------------------------------------------------

    final_score = min(
        round(
            forecast_score
            + official_alert_score,
            1,
        ),
        100.0,
    )

    category_rules = (
        RISK_RULES["risk_categories"]
    )

    if (
        final_score
        >= category_rules["high_threshold"]
    ):
        category = "HIGH"

    elif (
        final_score
        >= category_rules["medium_threshold"]
    ):
        category = "MEDIUM"

    else:
        category = "LOW"

    # --------------------------------------------------------
    # Combined hazards
    # --------------------------------------------------------

    hazard_reasons = []

    for hazard in forecast_hazards:
        if hazard not in hazard_reasons:
            hazard_reasons.append(hazard)

    for hazard in official_alert_hazards:
        if hazard not in hazard_reasons:
            hazard_reasons.append(hazard)

    if not hazard_reasons:
        hazard_reasons.append(
            "Clear / Safe Driving Conditions"
        )

    # --------------------------------------------------------
    # Risk-source metadata
    # --------------------------------------------------------

    risk_sources = []

    if forecast_score > 0:

        risk_sources.append(
            {
                "type": "forecast",
                "source": weather_source
                or "Open-Meteo",
                "forecast_time": forecast_time,
                "risk_score": forecast_score,
            }
        )

    if official_alert_score > 0:

        risk_sources.append(
            {
                "type": "official_alert",
                "source": "IMD CAP",
                "risk_score": official_alert_score,
                "alerts": official_alert_metadata,
            }
        )

    return {
        # Existing fields
        "risk_score": final_score,
        "risk_category": category,
        "hazards": hazard_reasons,

        # Forecast-derived risk
        "forecast_risk_score": (
            forecast_score
        ),
        "forecast_hazards": (
            forecast_hazards
        ),

        # Official alert risk
        "official_alert_risk_score": (
            official_alert_score
        ),
        "official_alert_hazards": (
            official_alert_hazards
        ),

        # Week 5 provenance
        "risk_sources": risk_sources,

        "official_alert_metadata": (
            official_alert_metadata
        ),
    }


# ============================================================
# ROUTE-LEVEL RISK
# ============================================================

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

            forecast_time=pt.get(
                "forecast_time"
            ),

            weather_source=pt.get(
                "weather_source"
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

    # --------------------------------------------------------
    # Overall route risk
    # --------------------------------------------------------

    if waypoints_weather:

        avg_route_risk = round(
            total_score
            / len(waypoints_weather),
            1,
        )

    else:

        avg_route_risk = 0.0

    # --------------------------------------------------------
    # Route safety status
    # --------------------------------------------------------

    route_rules = (
        RISK_RULES["route_safety"]
    )

    if (
        avg_route_risk
        > route_rules[
            "average_risk_threshold"
        ]
        or high_risk_segments
        >= route_rules[
            "high_risk_segment_limit"
        ]
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