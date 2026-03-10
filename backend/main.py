"""
Main FastAPI Application for AI Triage System

This module initializes the FastAPI application, sets up CORS middleware,
and includes all API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.triage_router import router as triage_router
from backend.ocr_router import router as ocr_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown events.
    
    Initializes the database on startup.
    """
    # Startup: Initialize database
    print("Initializing database...")
    init_db()
    print("Application startup complete!")
    
    yield
    
    # Shutdown: Cleanup (if needed)
    print("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="AI Triage System API",
    description="""
    AI-Based Emergency Triage Assistant API
    
    This API helps hospitals prioritize patients in emergency situations
    by analyzing patient symptoms, vital signs, and medical history.
    
    ## Features
    
    * **Triage Prediction**: ML-powered patient priority classification
    * **Patient Management**: Add and manage patient records
    * **Priority Queue**: View patients organized by urgency level
    * **Analytics**: Get statistics about patient queue
    
    ## Priority Levels
    
    * **Critical**: Immediate treatment required
    * **High**: Very urgent
    * **Medium**: Needs treatment soon
    * **Low**: Non-urgent
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
# Allow all origins for development - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(triage_router)
app.include_router(ocr_router)


@app.get("/")
async def root():
    """
    Root endpoint - API information and status.
    """
    return {
        "name": "AI Triage System API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "predict_triage": "/api/predict-triage",
            "patients": "/api/patients",
            "queue": "/api/patients/queue",
            "analytics": "/api/analytics/summary"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
