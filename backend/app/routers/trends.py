"""
Trends API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from ..database import get_db, Trend, Source, AnalyzedTrend
from ..schemas import Trend as TrendSchema, TrendList

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("", response_model=TrendList)
def get_trends(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    source: Optional[str] = None,
    analyzed_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get trends list with pagination and filters"""

    query = db.query(Trend).options(
        joinedload(Trend.source),
        joinedload(Trend.analysis).joinedload(AnalyzedTrend.solutions)
    )

    # Filter by source
    if source:
        query = query.join(Source).filter(Source.name == source)

    # Filter by analyzed status
    if analyzed_only:
        query = query.filter(Trend.analysis != None)

    # Order by collection time (newest first)
    query = query.order_by(Trend.collected_at.desc())

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * per_page
    trends = query.offset(offset).limit(per_page).all()

    return {
        "trends": trends,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/latest", response_model=TrendList)
def get_latest_trends(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get latest trends"""

    trends = db.query(Trend).options(
        joinedload(Trend.source),
        joinedload(Trend.analysis).joinedload(AnalyzedTrend.solutions)
    ).order_by(
        Trend.collected_at.desc()
    ).limit(limit).all()

    return {
        "trends": trends,
        "total": len(trends),
        "page": 1,
        "per_page": limit
    }


@router.get("/{trend_id}", response_model=TrendSchema)
def get_trend(trend_id: int, db: Session = Depends(get_db)):
    """Get trend by ID"""

    trend = db.query(Trend).options(
        joinedload(Trend.source),
        joinedload(Trend.analysis).joinedload(AnalyzedTrend.solutions)
    ).filter(Trend.id == trend_id).first()

    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    return trend
