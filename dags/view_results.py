#!/usr/bin/env python3
"""
트렌드 수집 결과 조회 스크립트
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sys
import os

# DB 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),  # Docker에서는 postgres 사용
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'airflow'),
    'user': os.getenv('DB_USER', 'airflow'),
    'password': os.getenv('DB_PASSWORD', 'airflow'),
}


def get_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(**DB_CONFIG)


def show_statistics():
    """통계 표시"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT t.id) as total_trends,
                    COUNT(DISTINCT at.id) as analyzed_trends,
                    COUNT(DISTINCT sol.id) as total_solutions,
                    ROUND(AVG(at.importance_score)::numeric, 1) as avg_importance
                FROM trends t
                LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                LEFT JOIN solutions sol ON at.id = sol.analyzed_trend_id
            """)

            stats = cur.fetchone()

            print("=" * 80)
            print("전체 통계")
            print("=" * 80)
            print(f"수집된 트렌드: {stats['total_trends']}개")
            print(f"분석 완료: {stats['analyzed_trends']}개")
            print(f"생성된 솔루션: {stats['total_solutions']}개")
            if stats['avg_importance']:
                print(f"평균 중요도: {float(stats['avg_importance'])}/10")
            print()


def show_recent_trends(limit=10):
    """최근 수집된 트렌드 표시"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    t.title,
                    t.category,
                    t.collected_at,
                    CASE
                        WHEN at.id IS NOT NULL THEN '분석완료'
                        ELSE '미분석'
                    END as status
                FROM trends t
                LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                ORDER BY t.collected_at DESC
                LIMIT %s
            """, (limit,))

            trends = cur.fetchall()

            print("=" * 80)
            print(f"최근 수집된 트렌드 (최대 {limit}개)")
            print("=" * 80)

            for idx, trend in enumerate(trends, 1):
                print(f"\n[{idx}] {trend['title']}")
                print(f"    카테고리: {trend['category']}")
                print(f"    수집시간: {trend['collected_at']}")
                print(f"    상태: {trend['status']}")


def show_analyzed_trends(limit=5):
    """분석된 트렌드 상세 정보"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    t.title,
                    at.summary,
                    at.category,
                    at.keywords,
                    at.problems,
                    at.importance_score,
                    at.sentiment,
                    at.analyzed_at
                FROM trends t
                JOIN analyzed_trends at ON t.id = at.trend_id
                ORDER BY at.analyzed_at DESC
                LIMIT %s
            """, (limit,))

            trends = cur.fetchall()

            print("\n" + "=" * 80)
            print(f"분석된 트렌드 상세 (최대 {limit}개)")
            print("=" * 80)

            for idx, trend in enumerate(trends, 1):
                print(f"\n[{idx}] {trend['title']}")
                print(f"    요약: {trend['summary']}")
                print(f"    카테고리: {trend['category']}")
                print(f"    키워드: {', '.join(trend['keywords'])}")
                print(f"    문제점: {', '.join(trend['problems'])}")
                print(f"    중요도: {trend['importance_score']}/10")
                print(f"    감정: {trend['sentiment']}")
                print(f"    분석시간: {trend['analyzed_at']}")


def show_solutions(limit=10):
    """생성된 솔루션 표시"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    t.title as trend_title,
                    s.title as solution_title,
                    s.description,
                    s.feasibility,
                    s.estimated_effort,
                    s.target_audience,
                    s.tech_stack
                FROM solutions s
                JOIN analyzed_trends at ON s.analyzed_trend_id = at.id
                JOIN trends t ON at.trend_id = t.id
                ORDER BY s.created_at DESC
                LIMIT %s
            """, (limit,))

            solutions = cur.fetchall()

            print("\n" + "=" * 80)
            print(f"생성된 솔루션 (최대 {limit}개)")
            print("=" * 80)

            for idx, sol in enumerate(solutions, 1):
                print(f"\n[{idx}] {sol['solution_title']}")
                print(f"    트렌드: {sol['trend_title']}")
                print(f"    설명: {sol['description']}")
                print(f"    실현가능성: {sol['feasibility']}")
                print(f"    예상기간: {sol['estimated_effort']}")
                print(f"    타겟: {sol['target_audience']}")
                print(f"    기술스택: {', '.join(sol['tech_stack'])}")


def main():
    """메인 함수"""
    try:
        show_statistics()
        show_recent_trends(limit=10)
        show_analyzed_trends(limit=5)
        show_solutions(limit=10)

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
