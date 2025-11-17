"""
Pain Points API Router
Pain Point 조회 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from .. import schemas

router = APIRouter(prefix="/api/pain-points", tags=["pain-points"])


@router.get("/", response_model=List[schemas.PainPoint])
def get_pain_points(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Pain Point 목록 조회"""
    query = """
        SELECT pp.*, rc.title as content_title, rc.url as content_url,
               s.name as source_name
        FROM pain_points pp
        JOIN raw_contents rc ON pp.content_id = rc.id
        JOIN sources s ON rc.source_id = s.id
        WHERE 1=1
    """

    params = []

    if severity:
        query += " AND pp.severity = %s"
        params.append(severity)

    if category:
        query += " AND pp.category = %s"
        params.append(category)

    if source:
        query += " AND s.name = %s"
        params.append(source)

    if min_confidence:
        query += " AND pp.confidence_score >= %s"
        params.append(min_confidence)

    query += " ORDER BY pp.analyzed_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    cursor = db.execute(query, params)
    results = cursor.fetchall()

    return [dict(row) for row in results]


@router.get("/stats")
def get_pain_point_stats(db: Session = Depends(get_db)):
    """Pain Point 통계"""
    query = """
        SELECT
            COUNT(*) as total_pain_points,
            AVG(confidence_score) as avg_confidence,
            COUNT(DISTINCT category) as categories_count,
            COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
            COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
            COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_count,
            COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_count
        FROM pain_points
    """

    cursor = db.execute(query)
    result = cursor.fetchone()

    return dict(result) if result else {}


@router.get("/{pain_point_id}", response_model=schemas.PainPointDetail)
def get_pain_point_detail(pain_point_id: int, db: Session = Depends(get_db)):
    """Pain Point 상세 정보"""
    query = """
        SELECT pp.*, rc.title, rc.body, rc.url, rc.author,
               s.name as source_name,
               COUNT(si.id) as ideas_count
        FROM pain_points pp
        JOIN raw_contents rc ON pp.content_id = rc.id
        JOIN sources s ON rc.source_id = s.id
        LEFT JOIN saas_ideas si ON pp.id = si.pain_point_id
        WHERE pp.id = %s
        GROUP BY pp.id, rc.id, s.id
    """

    cursor = db.execute(query, (pain_point_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Pain Point not found")

    return dict(result)
