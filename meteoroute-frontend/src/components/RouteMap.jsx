import React from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from "react-leaflet";
import L from "leaflet";

const createRiskMarkerIcon = (category) => {
  let color = "#22c55e"; // LOW
  if (category === "MEDIUM") color = "#f97316";
  if (category === "HIGH") color = "#ef4444";

  return L.divIcon({
    className: "custom-risk-icon",
    html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2.5px solid #ffffff; box-shadow: 0 0 6px rgba(0,0,0,0.7);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

export default function RouteMap({ waypoints }) {
  if (!waypoints || waypoints.length === 0) {
    return (
      <div className="w-full h-full min-h-[450px] flex flex-col items-center justify-center bg-gray-900 border border-gray-800 rounded-2xl text-gray-400 p-6 text-center">
        <p className="text-base font-medium">No active route rendered</p>
        <p className="text-xs text-gray-500 mt-1">
          Submit coordinates in the sidebar to visualize the route polyline and
          weather risk markers.
        </p>
      </div>
    );
  }

  const startPt = waypoints[0];
  const polylineCoords = waypoints.map((pt) => [pt.latitude, pt.longitude]);

  return (
    <MapContainer
      center={[startPt.latitude, startPt.longitude]}
      zoom={7}
      scrollWheelZoom={true}
      className="w-full h-full min-h-[450px] rounded-2xl shadow-2xl border border-gray-800"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polyline
        positions={polylineCoords}
        color="#3b82f6"
        weight={5}
        opacity={0.85}
      />

      {waypoints.map((pt, idx) => (
        <Marker
          key={idx}
          position={[pt.latitude, pt.longitude]}
          icon={createRiskMarkerIcon(pt.risk_category)}
        >
          <Popup>
            <div className="text-gray-900 text-xs p-1 space-y-1">
              <p className="font-bold text-sm text-gray-800">
                Waypoint #{idx + 1}
              </p>
              <p>
                <strong>Distance:</strong> {pt.distance_from_start_km} km
              </p>
              <p>
                <strong>ETA:</strong> +{pt.estimated_arrival_minutes} mins
              </p>
              <hr className="my-1 border-gray-300" />
              <p>
                <strong>Temp:</strong> {pt.temperature_c}°C |{" "}
                <strong>Wind:</strong> {pt.wind_speed_kmh} km/h
              </p>
              <p>
                <strong>Precipitation:</strong> {pt.precipitation_mm} mm
              </p>
              <p
                className="font-semibold text-xs mt-1"
                style={{
                  color:
                    pt.risk_category === "HIGH"
                      ? "#ef4444"
                      : pt.risk_category === "MEDIUM"
                        ? "#f97316"
                        : "#22c55e",
                }}
              >
                Risk: {pt.risk_category} ({pt.risk_score}/100)
              </p>
              <p className="text-[10px] text-gray-600 italic">
                Hazards: {pt.hazards.join(", ")}
              </p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
