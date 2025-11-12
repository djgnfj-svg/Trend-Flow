"""
Solutions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db, Solution, AnalyzedTrend, Trend
from ..schemas import Solution as SolutionSchema

router = APIRouter(prefix="/api/solutions", tags=["solutions"])


@router.get("", response_model=List[SolutionSchema])
def get_solutions(
    limit: int = Query(20, ge=1, le=100),
    feasibility: str = None,
    db: Session = Depends(get_db)
):
    """Get solutions list"""

    query = db.query(Solution)

    # Filter by feasibility
    if feasibility:
        query = query.filter(Solution.feasibility == feasibility)

    # Order by creation time (newest first)
    query = query.order_by(Solution.created_at.desc())

    solutions = query.limit(limit).all()

    return solutions


@router.get("/trend/{trend_id}", response_model=List[SolutionSchema])
def get_solutions_by_trend(trend_id: int, db: Session = Depends(get_db)):
    """Get solutions for a specific trend"""

    # Check if trend exists
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    # Get analyzed trend
    analyzed = db.query(AnalyzedTrend).filter(
        AnalyzedTrend.trend_id == trend_id
    ).first()

    if not analyzed:
        return []

    # Get solutions
    solutions = db.query(Solution).filter(
        Solution.analyzed_trend_id == analyzed.id
    ).all()

    return solutions
