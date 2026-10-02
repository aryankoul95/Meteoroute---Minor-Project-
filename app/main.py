from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_route import router as route_pipeline
from app.api_intent import router as intent_router
from app.api_natural_route import router as natural_route_router

app = FastAPI(title="MeteoRoute API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(route_pipeline, prefix="/api/v1")
app.include_router(intent_router, prefix="/api/v1")
app.include_router(natural_route_router, prefix="/api/v1")
