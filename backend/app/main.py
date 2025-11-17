"""
FastAPI Backend for Trend-Flow
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import stats, trends, solutions
try:
    from .routers import pain_points, saas_ideas
    PAIN_POINT_FINDER_ENABLED = True
except ImportError:
    PAIN_POINT_FINDER_ENABLED = False

app = FastAPI(
    title="Pain Point Finder API",
    description="API for Pain Point collection and SaaS idea generation",
    version="2.0.0"
)

# CORS 설정 (React 프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서 모든 origin 허용
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (기존)
app.include_router(stats.router)
app.include_router(trends.router)
app.include_router(solutions.router)

# Include new routers (Pain Point Finder)
if PAIN_POINT_FINDER_ENABLED:
    app.include_router(pain_points.router)
    app.include_router(saas_ideas.router)


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
