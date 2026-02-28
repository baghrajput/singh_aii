from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints.dashboard_api import router as dashboard_router
from app.database import create_db_and_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include dashboard API router
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}")

@app.on_event("startup")
async def startup():
    """
    Startup event to create database tables automatically.
    """
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Saudi Aramco AI Digital Assistant API is running"}
