from typing import Optional, Literal
from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's natural-language travel query")


class TravelIntent(BaseModel):
    language: Literal["English", "Hindi", "Unknown"]
    intent: Literal["route_planning", "weather_query", "unknown"]
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[str] = None
