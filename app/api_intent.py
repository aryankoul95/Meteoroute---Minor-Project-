from fastapi import APIRouter, HTTPException

from app.schemas.intent import IntentRequest, TravelIntent
from app.services.intent_extractor import extract_travel_intent_llm

router = APIRouter()


@router.post("/intent", response_model=TravelIntent)
async def extract_intent(payload: IntentRequest):
    try:
        return await extract_travel_intent_llm(payload.query)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )