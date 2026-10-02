import asyncio

from app.services.routing import (
    get_osrm_route,
    sample_waypoints,
)

from app.services.cap_parser import parse_cap_alert
from app.services.cap_normalizer import normalize_cap_alert
from app.services.cap_matcher import match_alerts_to_waypoints


CAP_TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
    <identifier>METEOROUTE-TIME-TEST-001</identifier>
    <sender>test@example.gov</sender>
    <sent>2026-10-02T10:00:00+05:30</sent>
    <status>Actual</status>
    <msgType>Alert</msgType>
    <scope>Public</scope>

    <info>
        <language>en-IN</language>
        <category>Met</category>
        <event>Heavy Rain</event>
        <urgency>Immediate</urgency>
        <severity>Severe</severity>
        <certainty>Likely</certainty>

        <effective>2026-10-02T10:00:00+05:30</effective>
        <expires>2026-10-03T23:59:00+05:30</expires>

        <senderName>Test Weather Authority</senderName>
        <headline>Heavy Rain Warning</headline>
        <description>Heavy rainfall is expected.</description>
        <instruction>Avoid unnecessary travel.</instruction>

        <area>
            <areaDesc>Jammu and Kashmir</areaDesc>

            <polygon>
                33.95,74.70
                34.25,74.70
                34.25,75.10
                33.95,75.10
            </polygon>
        </area>
    </info>
</alert>
"""


async def main():

    # Get Delhi → Srinagar route
    geometry, distance_km, duration_hrs = await get_osrm_route(
        28.6328027,
        77.2197713,
        34.0747444,
        74.8204443,
    )

    # Sample route waypoints
    sampled_points = sample_waypoints(
        geometry,
        15.0,
        duration_hrs,
        distance_km,
    )

    # Parse and normalize test CAP alert
    parsed_alert = parse_cap_alert(CAP_TEST_XML)
    normalized_alert = normalize_cap_alert(parsed_alert)

    cap_alerts = [normalized_alert]

    # Convert route points into matcher format
    route_waypoints = []

    for point in sampled_points:
        route_waypoints.append({
            "latitude": point["lat"],
            "longitude": point["lon"],
            "distance_from_start_km": point["dist_km"],
            "estimated_arrival_minutes": point["eta_min"],
        })

    # Departure time
    departure_time = "2026-10-03T08:00:00+05:30"

    # Match CAP alerts using:
    # 1. Spatial location
    # 2. Route arrival time
    matched = match_alerts_to_waypoints(
        route_waypoints,
        cap_alerts,
        departure_time,
    )

    # Count matched waypoints
    matched_count = sum(
        1
        for waypoint in matched
        if waypoint["cap_alerts"]
    )

    print("Route distance:", round(distance_km, 2), "km")
    print("Route duration:", round(duration_hrs, 2), "hours")
    print("Total waypoints:", len(route_waypoints))
    print("Departure time:", departure_time)
    print("CAP matched waypoints:", matched_count)

    # Print matched locations
    for waypoint in matched:
        if waypoint["cap_alerts"]:
            print(
                "MATCH:",
                round(waypoint["latitude"], 6),
                round(waypoint["longitude"], 6),
            )


if __name__ == "__main__":
    asyncio.run(main())