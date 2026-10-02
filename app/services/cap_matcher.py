from datetime import datetime, timedelta, timezone
from math import radians, sin, cos, sqrt, atan2
from typing import Optional


IST = timezone(timedelta(hours=5, minutes=30))


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=IST)

        return parsed

    except (ValueError, TypeError):
        return None


def _parse_polygon(polygon_text: Optional[str]) -> list[tuple[float, float]]:
    if not polygon_text:
        return []

    points = []

    for pair in polygon_text.split():

        try:
            latitude, longitude = pair.split(",")

            points.append(
                (
                    float(latitude),
                    float(longitude),
                )
            )

        except (ValueError, TypeError):
            continue

    return points


def _point_in_polygon(
    latitude: float,
    longitude: float,
    polygon: list[tuple[float, float]],
) -> bool:

    if len(polygon) < 3:
        return False

    inside = False

    j = len(polygon) - 1

    for i in range(len(polygon)):

        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]

        if (
            (lon_i > longitude)
            != (lon_j > longitude)
        ):

            intersection_lat = (
                (lat_j - lat_i)
                * (longitude - lon_i)
                / (lon_j - lon_i)
                + lat_i
            )

            if latitude < intersection_lat:
                inside = not inside

        j = i

    return inside


def _distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:

    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius_km * c


def _match_circle(
    latitude: float,
    longitude: float,
    circle_text: Optional[str],
) -> bool:

    if not circle_text:
        return False

    try:

        center, radius_text = circle_text.split()

        center_lat, center_lon = center.split(",")

        radius_km = float(radius_text)

        distance = _distance_km(
            latitude,
            longitude,
            float(center_lat),
            float(center_lon),
        )

        return distance <= radius_km

    except (ValueError, TypeError):
        return False


# -------------------------------------------------
# Temporal matching
# -------------------------------------------------

def _alert_valid_at_time(
    alert: dict,
    arrival_time: Optional[datetime],
) -> bool:

    # If journey arrival time is unavailable,
    # preserve spatial matching behaviour.
    if arrival_time is None:
        return True

    for info in alert.get("info", []):

        effective = _parse_datetime(
            info.get("effective")
        )

        expires = _parse_datetime(
            info.get("expires")
        )

        # If the alert has not started yet
        if effective and arrival_time < effective:
            continue

        # If the alert has already expired
        if expires and arrival_time > expires:
            continue

        # Alert is valid at arrival time
        return True

    return False


# -------------------------------------------------
# Spatial + temporal alert matching
# -------------------------------------------------

def waypoint_matches_alert(
    latitude: float,
    longitude: float,
    alert: dict,
    arrival_time: Optional[datetime] = None,
) -> bool:

    # First check temporal validity
    if not _alert_valid_at_time(
        alert,
        arrival_time,
    ):
        return False

    for info in alert.get("info", []):

        area = info.get("area", {})

        # -----------------------------
        # Polygon matching
        # -----------------------------

        polygon = _parse_polygon(
            area.get("polygon")
        )

        if polygon and _point_in_polygon(
            latitude,
            longitude,
            polygon,
        ):
            return True

        # -----------------------------
        # Circle matching
        # -----------------------------

        if _match_circle(
            latitude,
            longitude,
            area.get("circle"),
        ):
            return True

    return False


def match_alerts_to_waypoint(
    waypoint: dict,
    alerts: list[dict],
    departure_time: Optional[str] = None,
) -> dict:

    latitude = waypoint["latitude"]
    longitude = waypoint["longitude"]

    estimated_arrival_minutes = waypoint.get(
        "estimated_arrival_minutes",
        0.0,
    )

    arrival_time = None

    if departure_time:

        departure = _parse_datetime(
            departure_time
        )

        if departure:

            arrival_time = (
                departure
                + timedelta(
                    minutes=estimated_arrival_minutes
                )
            )

    matched_alerts = []

    for alert in alerts:

        if waypoint_matches_alert(
            latitude,
            longitude,
            alert,
            arrival_time,
        ):

            matched_alerts.append(
                alert
            )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "cap_alerts": matched_alerts,
    }


def match_alerts_to_waypoints(
    waypoints: list[dict],
    alerts: list[dict],
    departure_time: Optional[str] = None,
) -> list[dict]:

    results = []

    for waypoint in waypoints:

        results.append(
            match_alerts_to_waypoint(
                waypoint,
                alerts,
                departure_time,
            )
        )

    return results