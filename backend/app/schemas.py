"""
Pydantic schemas for API validation
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class SourceBase(BaseModel):
    name: str
    category: Optional[str] = None


class Source(SourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SolutionBase(BaseModel):
    title: str
    description: str
    feasibility: Optional[str] = None
    estimated_effort: Optional[str] = None
    target_audience: Optional[str] = None
    tech_stack: Optional[List[str]] = []


class Solution(SolutionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalyzedTrendBase(BaseModel):
    summary: str
    category: Optional[str] = None
    problems: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    sentiment: Optional[str] = None
    importance_score: Optional[int] = None


class AnalyzedTrend(AnalyzedTrendBase):
    id: int
    analyzed_at: Optional[datetime] = None
    solutions: List[Solution] = []

    model_config = ConfigDict(from_attributes=True)


class TrendBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    rank: Optional[int] = None


class Trend(TrendBase):
    id: int
    source_id: int
    collected_at: Optional[datetime] = None
    trend_metadata: Optional[dict] = {}
    source: Optional[Source] = None
    analysis: Optional[AnalyzedTrend] = None

    model_config = ConfigDict(from_attributes=True)


class TrendList(BaseModel):
    trends: List[Trend]
    total: int
    page: int
    per_page: int


class Stats(BaseModel):
    total_trends: int
    analyzed_trends: int
    total_solutions: int
    avg_importance: Optional[float] = None


class DailyStats(BaseModel):
    date: str
    source_name: str
    trend_count: int
    analyzed_count: int
    solution_count: int
    avg_importance: Optional[float] = None
