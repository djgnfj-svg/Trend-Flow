"""
Statistics API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List
from datetime import date

from ..database import get_db, Trend, AnalyzedTrend, Solution
from ..schemas import Stats, DailyStats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview", response_model=Stats)
def get_overview_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""

    total_trends = db.query(func.count(distinct(Trend.id))).scalar()
    analyzed_trends = db.query(func.count(distinct(AnalyzedTrend.id))).scalar()
    total_solutions = db.query(func.count(distinct(Solution.id))).scalar()
    avg_importance = db.query(func.avg(AnalyzedTrend.importance_score)).scalar()

    return {
        "total_trends": total_trends or 0,
        "analyzed_trends": analyzed_trends or 0,
        "total_solutions": total_solutions or 0,
        "avg_importance": float(avg_importance) if avg_importance else None
    }


@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(limit: int = 30, db: Session = Depends(get_db)):
    """Get daily statistics"""

    query = db.query(
        func.date(Trend.collected_at).label('date'),
        func.count(distinct(Trend.id)).label('trend_count'),
        func.count(distinct(AnalyzedTrend.id)).label('analyzed_count'),
        func.count(distinct(Solution.id)).label('solution_count'),
        func.avg(AnalyzedTrend.importance_score).label('avg_importance')
    ).outerjoin(
        AnalyzedTrend, Trend.id == AnalyzedTrend.trend_id
    ).outerjoin(
        Solution, AnalyzedTrend.id == Solution.analyzed_trend_id
    ).group_by(
        func.date(Trend.collected_at)
    ).order_by(
        func.date(Trend.collected_at).desc()
    ).limit(limit)

    results = []
    for row in query.all():
        results.append({
            "date": str(row.date),
            "source_name": "all",
            "trend_count": row.trend_count or 0,
            "analyzed_count": row.analyzed_count or 0,
            "solution_count": row.solution_count or 0,
            "avg_importance": float(row.avg_importance) if row.avg_importance else None
        })

    return results
