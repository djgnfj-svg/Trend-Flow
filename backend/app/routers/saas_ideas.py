"""
SaaS Ideas API Router
SaaS 아이디어 조회 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import schemas

router = APIRouter(prefix="/api/ideas", tags=["ideas"])


@router.get("/", response_model=List[schemas.SaaSIdea])
def get_saas_ideas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_score: Optional[int] = Query(None, ge=1, le=10),
    business_model: Optional[str] = None,
    complexity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """SaaS 아이디어 목록 조회"""
    query = """
        SELECT si.*, pp.problem_statement, pp.severity, pp.affected_users,
               s.name as source_name,
               mv.validation_score, mv.market_status
        FROM saas_ideas si
        JOIN pain_points pp ON si.pain_point_id = pp.id
        JOIN raw_contents rc ON pp.content_id = rc.id
        JOIN sources s ON rc.source_id = s.id
        LEFT JOIN market_validation mv ON si.id = mv.idea_id
        WHERE 1=1
    """

    params = []

    if min_score:
        query += " AND si.overall_score >= %s"
        params.append(min_score)

    if business_model:
        query += " AND si.business_model = %s"
        params.append(business_model)

    if complexity:
        query += " AND si.complexity = %s"
        params.append(complexity)

    query += " ORDER BY si.overall_score DESC, si.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    cursor = db.execute(query, params)
    results = cursor.fetchall()

    return [dict(row) for row in results]


@router.get("/top")
def get_top_ideas(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """최고 점수 아이디어 (v_top_ideas 뷰 사용)"""
    query = """
        SELECT * FROM v_top_ideas
        LIMIT %s
    """

    cursor = db.execute(query, (limit,))
    results = cursor.fetchall()

    return [dict(row) for row in results]


@router.get("/{idea_id}", response_model=schemas.SaaSIdeaDetail)
def get_idea_detail(idea_id: int, db: Session = Depends(get_db)):
    """SaaS 아이디어 상세 정보"""
    query = """
        SELECT si.*, pp.problem_statement, pp.problem_detail,
               pp.affected_users, pp.severity, pp.frequency,
               pp.market_size, pp.existing_solutions,
               rc.title as original_title, rc.url as original_url,
               s.name as source_name,
               mv.search_volume_score, mv.trend_direction, mv.competitor_count,
               mv.competitors, mv.saturation_score, mv.market_status,
               mv.validation_score, mv.recommendation, mv.validated_at
        FROM saas_ideas si
        JOIN pain_points pp ON si.pain_point_id = pp.id
        JOIN raw_contents rc ON pp.content_id = rc.id
        JOIN sources s ON rc.source_id = s.id
        LEFT JOIN market_validation mv ON si.id = mv.idea_id
        WHERE si.id = %s
    """

    cursor = db.execute(query, (idea_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="SaaS Idea not found")

    return dict(result)


@router.get("/stats/overview")
def get_ideas_stats(db: Session = Depends(get_db)):
    """아이디어 통계"""
    query = """
        SELECT
            COUNT(*) as total_ideas,
            AVG(overall_score) as avg_score,
            AVG(feasibility_score) as avg_feasibility,
            AVG(market_score) as avg_market,
            COUNT(CASE WHEN complexity = 'simple' THEN 1 END) as simple_count,
            COUNT(CASE WHEN complexity = 'moderate' THEN 1 END) as moderate_count,
            COUNT(CASE WHEN complexity = 'complex' THEN 1 END) as complex_count,
            COUNT(CASE WHEN overall_score >= 8 THEN 1 END) as high_score_count
        FROM saas_ideas
    """

    cursor = db.execute(query)
    result = cursor.fetchone()

    return dict(result) if result else {}
