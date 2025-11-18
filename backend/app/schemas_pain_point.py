"""
Pydantic Schemas for Pain Point Finder
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Pain Point Schemas
class PainPointBase(BaseModel):
    problem_statement: str
    problem_detail: Optional[str] = None
    affected_users: Optional[str] = None
    frequency: Optional[str] = None
    severity: Optional[str] = None
    market_size: Optional[str] = None
    willingness_to_pay: Optional[str] = None
    existing_solutions: Optional[List[str]] = []
    solution_gaps: Optional[str] = None
    keywords: Optional[List[str]] = []
    category: Optional[str] = None
    confidence_score: Optional[float] = None


class PainPoint(PainPointBase):
    id: int
    content_id: int
    analyzed_at: datetime
    created_at: datetime
    content_title: Optional[str] = None
    content_url: Optional[str] = None
    source_name: Optional[str] = None

    class Config:
        from_attributes = True


class PainPointDetail(PainPoint):
    title: str
    body: str
    url: Optional[str] = None
    author: Optional[str] = None
    ideas_count: int = 0


# SaaS Idea Schemas
class SaaSIdeaBase(BaseModel):
    title: str
    tagline: Optional[str] = None
    description: str
    business_model: Optional[str] = None
    pricing_model: Optional[str] = None
    estimated_monthly_revenue: Optional[str] = None
    tech_stack: Optional[List[str]] = []
    complexity: Optional[str] = None
    estimated_dev_time: Optional[str] = None
    mvp_features: Optional[List[str]] = []
    mvp_description: Optional[str] = None
    target_audience: Optional[str] = None
    go_to_market_strategy: Optional[str] = None
    competition_level: Optional[str] = None
    differentiation: Optional[str] = None
    feasibility_score: Optional[int] = None
    market_score: Optional[int] = None
    overall_score: Optional[int] = None
    tags: Optional[List[str]] = []
    similar_products: Optional[List[str]] = []


class SaaSIdea(SaaSIdeaBase):
    id: int
    pain_point_id: int
    created_at: datetime
    problem_statement: Optional[str] = None
    severity: Optional[str] = None
    affected_users: Optional[str] = None
    source_name: Optional[str] = None

    class Config:
        from_attributes = True


class SaaSIdeaDetail(SaaSIdea):
    problem_detail: Optional[str] = None
    frequency: Optional[str] = None
    market_size: Optional[str] = None
    existing_solutions: Optional[List[str]] = []
    original_title: Optional[str] = None
    original_url: Optional[str] = None


# Stats Schemas
class PainPointStats(BaseModel):
    total_pain_points: int
    avg_confidence: Optional[float] = None
    categories_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class SaaSIdeaStats(BaseModel):
    total_ideas: int
    avg_score: Optional[float] = None
    avg_feasibility: Optional[float] = None
    avg_market: Optional[float] = None
    simple_count: int
    moderate_count: int
    complex_count: int
    high_score_count: int


class DashboardStats(BaseModel):
    total_contents: int
    total_pain_points: int
    total_ideas: int
    avg_confidence: Optional[float] = None
    avg_idea_score: Optional[float] = None
