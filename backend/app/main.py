
from fastapi import FastAPI, HTTPException
from backend.app.database import get_connection
from backend.app.routers.analytics import router as analytics_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="PicoGrid API",
    description="IoT Energy Monitoring and Analytics Platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analytics_router)

@app.get("/")
def home():
    return {
        "project": "PicoGrid",
        "message": "Energy Monitoring API is running",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "not_checked"
    }

@app.get("/health/database")
def database_health_check():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "database_name": "picogrid_db"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {type(error).__name__}"
        )
