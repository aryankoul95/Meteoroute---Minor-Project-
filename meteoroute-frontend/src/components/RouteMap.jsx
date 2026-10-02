import React from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from "react-leaflet";
import L from "leaflet";

const getRiskColor = (category) => {
  if (category === "HIGH") return "#ef4444";
  if (category === "MEDIUM") return "#f97316";
  return "#22c55e";
};

const createRiskMarkerIcon = (category) => {
  const color = getRiskColor(category);

  return L.divIcon({
    className: "custom-risk-icon",
    html: `
      <div style="
        background-color: ${color};
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2.5px solid #ffffff;
        box-shadow: 0 0 6px rgba(0,0,0,0.7);
      "></div>
    `,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

export default function RouteMap({ waypoints, segments }) {
  if (!waypoints || waypoints.length === 0) {
    return (
      <div className="w-full h-full min-h-[450px] flex flex-col items-center justify-center bg-gray-900 border border-gray-800 rounded-2xl text-gray-400 p-6 text-center">
        <p className="text-base font-medium">
          No active route rendered
        </p>

        <p className="text-xs text-gray-500 mt-1">
          Submit a natural-language travel query to visualize the
          weather-aware route.
        </p>
      </div>
    );
  }

  const startPt = waypoints[0];

  /*
   * If segment data is available, draw every segment
   * using its calculated risk category.
   */
  const hasSegments =
    Array.isArray(segments) && segments.length > 0;

  return (
    <MapContainer
      center={[
        startPt.latitude,
        startPt.longitude,
      ]}
      zoom={7}
      scrollWheelZoom={true}
      className="w-full h-full min-h-[450px] rounded-2xl shadow-2xl border border-gray-800"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {hasSegments ? (
        segments.map((segment) => (
          <Polyline
            key={segment.segment_id}
            positions={[
              [
                segment.start.lat,
                segment.start.lon,
              ],
              [
                segment.end.lat,
                segment.end.lon,
              ],
            ]}
            color={getRiskColor(
              segment.risk_category
            )}
            weight={6}
            opacity={0.9}
          >
            <Popup>
              <div className="text-gray-900 text-xs p-1 space-y-1">
                <p className="font-bold text-sm">
                  Route Segment #{segment.segment_id}
                </p>

                <p>
                  <strong>Distance:</strong>{" "}
                  {segment.distance_km} km
                </p>

                <p>
                  <strong>ETA:</strong>{" "}
                  +{segment.start_eta_min} →{" "}
                  +{segment.end_eta_min} mins
                </p>

                <hr className="my-1 border-gray-300" />

                <p
                  className="font-semibold"
                  style={{
                    color: getRiskColor(
                      segment.risk_category
                    ),
                  }}
                >
                  Risk: {segment.risk_category} (
                  {segment.risk_score}/100)
                </p>

                <p className="text-[10px] text-gray-600 italic">
                  Hazards:{" "}
                  {segment.hazards &&
                  segment.hazards.length > 0
                    ? segment.hazards.join(", ")
                    : "None detected"}
                </p>
              </div>
            </Popup>
          </Polyline>
        ))
      ) : (
        /*
         * Fallback for older route responses.
         */
        <Polyline
          positions={waypoints.map((pt) => [
            pt.latitude,
            pt.longitude,
          ])}
          color="#3b82f6"
          weight={5}
          opacity={0.85}
        />
      )}

      {waypoints.map((pt, idx) => (
        <Marker
          key={idx}
          position={[
            pt.latitude,
            pt.longitude,
          ]}
          icon={createRiskMarkerIcon(
            pt.risk_category
          )}
        >
          <Popup>
            <div className="text-gray-900 text-xs p-1 space-y-1">
              <p className="font-bold text-sm text-gray-800">
                Waypoint #{idx + 1}
              </p>

              <p>
                <strong>Distance:</strong>{" "}
                {pt.distance_from_start_km} km
              </p>

              <p>
                <strong>ETA:</strong>{" "}
                +{pt.estimated_arrival_minutes} mins
              </p>

              <hr className="my-1 border-gray-300" />

              <p>
                <strong>Temperature at arrival:</strong>{" "}
                {pt.temperature_c ?? "N/A"}°C
              </p>

              <p>
                <strong>Wind:</strong>{" "}
                {pt.wind_speed_kmh ?? "N/A"} km/h
              </p>

              <p>
                <strong>Precipitation:</strong>{" "}
                {pt.precipitation_mm ?? "N/A"} mm
              </p>

              <p
                className="font-semibold text-xs mt-1"
                style={{
                  color: getRiskColor(
                    pt.risk_category
                  ),
                }}
              >
                Risk: {pt.risk_category} (
                {pt.risk_score}/100)
              </p>

              <p className="text-[10px] text-gray-600 italic">
                Hazards:{" "}
                {pt.hazards &&
                pt.hazards.length > 0
                  ? pt.hazards.join(", ")
                  : "None detected"}
              </p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}