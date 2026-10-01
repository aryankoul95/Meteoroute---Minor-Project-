import React, { useState } from "react";
import axios from "axios";
import RouteMap from "./components/RouteMap";
import {
  Navigation,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Play,
} from "lucide-react";

export default function App() {
  const [startLat, setStartLat] = useState(28.6139);
  const [startLon, setStartLon] = useState(77.209);
  const [endLat, setEndLat] = useState(26.9124);
  const [endLon, setEndLon] = useState(75.7873);
  const [intervalKm, setIntervalKm] = useState(15.0);

  const [loading, setLoading] = useState(false);
  const [routeData, setRouteData] = useState(null);
  const [error, setError] = useState(null);

  const handleRunPipeline = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/v1/route-pipeline",
        {
          start_lat: parseFloat(startLat),
          start_lon: parseFloat(startLon),
          end_lat: parseFloat(endLat),
          end_lon: parseFloat(endLon),
          sampling_interval_km: parseFloat(intervalKm),
        },
      );
      setRouteData(res.data);
    } catch (err) {
      console.error(err);
      setError(
        "Could not connect to FastAPI server. Ensure uvicorn is running on port 8000.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans">
      <header className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600/20 border border-blue-500/30 rounded-xl">
            <Navigation className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              MeteoRoute
            </h1>
            <p className="text-[11px] text-gray-400">
              Spatiotemporal Weather Risk Dashboard
            </p>
          </div>
        </div>
        <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-medium flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>{" "}
          Backend Engine Connected
        </span>
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 p-6 max-w-[1800px] w-full mx-auto">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2 text-gray-200">
              <Navigation className="w-4 h-4 text-blue-400" /> Route Coordinates
            </h2>

            <form onSubmit={handleRunPipeline} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-400 mb-1 block">
                  Origin (Lat, Lon)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    step="any"
                    value={startLat}
                    onChange={(e) => setStartLat(e.target.value)}
                    placeholder="Lat"
                    className="bg-gray-800 border border-gray-700 text-sm rounded-lg p-2.5 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                  <input
                    type="number"
                    step="any"
                    value={startLon}
                    onChange={(e) => setStartLon(e.target.value)}
                    placeholder="Lon"
                    className="bg-gray-800 border border-gray-700 text-sm rounded-lg p-2.5 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-400 mb-1 block">
                  Destination (Lat, Lon)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    step="any"
                    value={endLat}
                    onChange={(e) => setEndLat(e.target.value)}
                    placeholder="Lat"
                    className="bg-gray-800 border border-gray-700 text-sm rounded-lg p-2.5 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                  <input
                    type="number"
                    step="any"
                    value={endLon}
                    onChange={(e) => setEndLon(e.target.value)}
                    placeholder="Lon"
                    className="bg-gray-800 border border-gray-700 text-sm rounded-lg p-2.5 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-400 mb-1 block">
                  Sampling Interval (km)
                </label>
                <input
                  type="number"
                  step="any"
                  value={intervalKm}
                  onChange={(e) => setIntervalKm(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-sm rounded-lg p-2.5 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  "Fetching Spatiotemporal Pipeline..."
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" /> Compute Weather
                    Route
                  </>
                )}
              </button>
            </form>

            {error && (
              <p className="text-red-400 text-xs mt-3 bg-red-500/10 border border-red-500/20 p-2.5 rounded-lg">
                {error}
              </p>
            )}
          </div>

          {routeData && (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-4">
              <h3 className="text-base font-semibold flex items-center gap-2 text-gray-200">
                <ShieldAlert className="w-4 h-4 text-indigo-400" /> Route
                Analysis Summary
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-800/60 p-3 rounded-xl border border-gray-700/50">
                  <span className="text-[11px] text-gray-400 block">
                    Total Distance
                  </span>
                  <span className="text-lg font-bold text-gray-100">
                    {routeData.total_distance_km} km
                  </span>
                </div>
                <div className="bg-gray-800/60 p-3 rounded-xl border border-gray-700/50">
                  <span className="text-[11px] text-gray-400 block">
                    Est. Duration
                  </span>
                  <span className="text-lg font-bold text-gray-100">
                    {routeData.total_duration_hours} hrs
                  </span>
                </div>
                <div className="bg-gray-800/60 p-3 rounded-xl border border-gray-700/50">
                  <span className="text-[11px] text-gray-400 block">
                    Waypoints Sampled
                  </span>
                  <span className="text-lg font-bold text-blue-400">
                    {routeData.total_waypoints_sampled}
                  </span>
                </div>
                <div className="bg-gray-800/60 p-3 rounded-xl border border-gray-700/50">
                  <span className="text-[11px] text-gray-400 block">
                    Overall Risk Score
                  </span>
                  <span className="text-lg font-bold text-amber-400">
                    {routeData.overall_route_risk_score} / 100
                  </span>
                </div>
              </div>

              <div
                className={`p-3.5 rounded-xl border flex items-center justify-between ${
                  routeData.route_safety_status === "SAFE"
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                    : "bg-red-500/10 border-red-500/30 text-red-400"
                }`}
              >
                <span className="text-xs font-medium">Safety Status</span>
                <span className="font-bold text-sm flex items-center gap-1">
                  {routeData.route_safety_status === "SAFE" ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  {routeData.route_safety_status}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-3 flex flex-col h-[calc(100vh-120px)] min-h-[500px]">
          <RouteMap waypoints={routeData?.waypoints} />
        </div>
      </main>
    </div>
  );
}
