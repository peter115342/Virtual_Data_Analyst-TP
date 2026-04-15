from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.cache import redis_client
from app.config import settings
from app.database import connection, mongo, chat_history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    if settings.database_url:
        connection.db_manager = connection.DatabaseManager(
            database_url=settings.database_url, readonly=settings.database_readonly
        )
        await connection.db_manager.connect()
        print("Database connected")
    else:
        print("No DATABASE_URL provided - use /api/connect-database endpoint to connect")

    try:
        await mongo.connect()
        await chat_history.ensure_indexes()
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

    await redis_client.connect()

    yield

    if connection.db_manager:
        await connection.db_manager.disconnect()
        print("Database disconnected")

    await mongo.disconnect()
    await redis_client.disconnect()


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

    try:
        mongo.get_db()
        mongo_status = "connected"
    except RuntimeError:
        mongo_status = "not connected"

    redis_status = "connected" if redis_client.is_connected() else "not connected"

    return {
        "status": "healthy",
        "database": db_status,
        "mongodb": mongo_status,
        "redis": redis_status,
    }
