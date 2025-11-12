"""
FastAPI Backend for Trend-Flow
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import stats, trends, solutions

app = FastAPI(
    title="Trend-Flow API",
    description="API for trend collection and analysis",
    version="1.0.0"
)

# CORS 설정 (React 프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],  # React/Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stats.router)
app.include_router(trends.router)
app.include_router(solutions.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Trend-Flow API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
