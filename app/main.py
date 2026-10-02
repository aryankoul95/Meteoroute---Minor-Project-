from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_route import router as route_pipeline
from app.api_intent import router as intent_router

app = FastAPI(title="MeteoRoute API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing route pipeline
app.include_router(route_pipeline, prefix="/api/v1")

# Include Week 2 multilingual intent pipeline
app.include_router(intent_router, prefix="/api/v1")
