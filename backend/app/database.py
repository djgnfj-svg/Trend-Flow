"""
Database connection and models
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ARRAY, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://airflow:airflow@postgres:5432/airflow"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    url = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    trends = relationship("Trend", back_populates="source")


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(Text, nullable=False)
    description = Column(Text)
    url = Column(Text)
    category = Column(String(100))
    rank = Column(Integer)
    trend_metadata = Column("metadata", JSON)  # SQLAlchemy 예약어 회피
    collected_at = Column(DateTime)
    collected_date = Column(DateTime)
    created_at = Column(DateTime)

    source = relationship("Source", back_populates="trends")
    analysis = relationship("AnalyzedTrend", back_populates="trend", uselist=False)


class AnalyzedTrend(Base):
    __tablename__ = "analyzed_trends"

    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, ForeignKey("trends.id"))
    summary = Column(Text, nullable=False)
    category = Column(String(100))
    problems = Column(ARRAY(Text))
    keywords = Column(ARRAY(Text))
    sentiment = Column(String(20))
    importance_score = Column(Integer)
    analyzed_at = Column(DateTime)
    created_at = Column(DateTime)

    trend = relationship("Trend", back_populates="analysis")
    solutions = relationship("Solution", back_populates="analyzed_trend")


class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True)
    analyzed_trend_id = Column(Integer, ForeignKey("analyzed_trends.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    feasibility = Column(String(20))
    estimated_effort = Column(String(20))
    target_audience = Column(Text)
    tech_stack = Column(ARRAY(Text))
    created_at = Column(DateTime)

    analyzed_trend = relationship("AnalyzedTrend", back_populates="solutions")


# Dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
