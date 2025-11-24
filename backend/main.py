# Main FastAPI application

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.database import connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    connection.db_manager = connection.DatabaseManager(
        database_url=settings.database_url, readonly=settings.database_readonly
    )
    await connection.db_manager.connect()
    print("Database connected")

    yield

    await connection.db_manager.disconnect()
    print("Database disconnected")


app = FastAPI(
    title="Virtual Data Analyst API",
    description="GenAI-powered dashboard generator backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Virtual Data Analyst API is running"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint with database status
    """
    db_status = "connected" if connection.db_manager else "not initialized"

    return {"status": "healthy", "database": db_status}
