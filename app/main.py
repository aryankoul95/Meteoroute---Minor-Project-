from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_route import router as route_pipeline

app = FastAPI(title="MeteoRoute API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the endpoint router
app.include_router(route_pipeline, prefix="/api/v1")