from pydantic import BaseModel, Field
from typing import List, Optional

class RouteRequest(BaseModel):
    start_lat: float = Field(..., example=28.6139)
    start_lon: float = Field(..., example=77.2090)
    end_lat: float = Field(..., example=26.9124)
    end_lon: float = Field(..., example=75.7873)
    sampling_interval_km: Optional[float] = Field(15.0)

class WaypointWeatherRisk(BaseModel):
    latitude: float
    longitude: float
    distance_from_start_km: float
    estimated_arrival_minutes: float
    temperature_c: float
    wind_speed_kmh: float
    precipitation_mm: float
    weather_code: int
    risk_score: float
    risk_category: str
    hazards: List[str]

class RouteResponse(BaseModel):
    total_distance_km: float
    total_duration_hours: float
    total_waypoints_sampled: int
    overall_route_risk_score: float
    high_risk_segments_count: int
    route_safety_status: str
    waypoints: List[WaypointWeatherRisk]