"""
데이터베이스 관리 모듈
"""
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from typing import List, Dict, Optional
import logging
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


class DatabaseManager:
    """PostgreSQL 데이터베이스 관리 클래스"""

    def __init__(self, **kwargs):
        """
        데이터베이스 연결 초기화

        Args:
            **kwargs: 데이터베이스 연결 파라미터 (선택사항)
                     제공되지 않으면 config.py의 DATABASE_CONFIG 사용
        """
        self.connection_params = {**DATABASE_CONFIG, **kwargs}

    def get_connection(self):
        """데이터베이스 연결 생성"""
        return psycopg2.connect(**self.connection_params)

    def get_source_id(self, source_name: str) -> Optional[int]:
        """소스 이름으로 ID 조회"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                result = cur.fetchone()
                return result[0] if result else None

    def save_trends(self, source_name: str, trends: List[Dict]) -> int:
        """
        트렌드 데이터를 데이터베이스에 저장

        Args:
            source_name: 소스 이름 (예: 'github_trending')
            trends: 트렌드 데이터 리스트

        Returns:
            저장된 트렌드 개수
        """
        source_id = self.get_source_id(source_name)
        if not source_id:
            raise ValueError(f"Source '{source_name}' not found in database")

        saved_count = 0
        skipped_count = 0

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for trend in trends:
                    try:
                        cur.execute("""
                            INSERT INTO trends (
                                source_id, title, description, url,
                                category, rank, metadata
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (source_id, title, collected_date)
                            DO NOTHING
                            RETURNING id
                        """, (
                            source_id,
                            trend['title'],
                            trend.get('description'),
                            trend.get('url'),
                            trend.get('category'),
                            trend.get('rank'),
                            Json(trend.get('metadata', {}))
                        ))

                        result = cur.fetchone()
                        if result:
                            saved_count += 1
                            logger.info(f"저장됨: {trend['title']}")
                        else:
                            skipped_count += 1
                            logger.debug(f"중복 스킵: {trend['title']}")

                    except Exception as e:
                        logger.warning(f"저장 실패 ({trend.get('title')}): {str(e)}")
                        continue

                conn.commit()

        logger.info(f"저장 완료: {saved_count}개 저장, {skipped_count}개 스킵")
        return saved_count

    def get_unanalyzed_trends(self, limit: Optional[int] = None, source_name: Optional[str] = None) -> List[Dict]:
        """
        아직 분석되지 않은 트렌드 가져오기

        Args:
            limit: 가져올 최대 개수 (None이면 전부)
            source_name: 특정 소스만 필터링 (선택사항)

        Returns:
            분석되지 않은 트렌드 리스트
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if source_name:
                    query = """
                        SELECT t.id, t.title, t.description, t.url,
                               t.category, t.rank, t.metadata,
                               s.name as source_name
                        FROM trends t
                        JOIN sources s ON t.source_id = s.id
                        LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                        WHERE at.id IS NULL AND s.name = %s
                        ORDER BY t.collected_at DESC
                    """
                    if limit:
                        query += " LIMIT %s"
                        cur.execute(query, (source_name, limit))
                    else:
                        cur.execute(query, (source_name,))
                else:
                    query = """
                        SELECT t.id, t.title, t.description, t.url,
                               t.category, t.rank, t.metadata,
                               s.name as source_name
                        FROM trends t
                        JOIN sources s ON t.source_id = s.id
                        LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                        WHERE at.id IS NULL
                        ORDER BY t.collected_at DESC
                    """
                    if limit:
                        query += " LIMIT %s"
                        cur.execute(query, (limit,))
                    else:
                        cur.execute(query)

                trends = cur.fetchall()
                return [dict(trend) for trend in trends]

    def save_analysis(self, trend_id: int, analysis: Dict) -> int:
        """
        AI 분석 결과 저장

        Args:
            trend_id: 트렌드 ID
            analysis: 분석 결과 딕셔너리

        Returns:
            분석 결과 ID
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO analyzed_trends (
                        trend_id, summary, category, problems,
                        keywords, sentiment, importance_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (trend_id)
                    DO UPDATE SET
                        summary = EXCLUDED.summary,
                        category = EXCLUDED.category,
                        problems = EXCLUDED.problems,
                        keywords = EXCLUDED.keywords,
                        sentiment = EXCLUDED.sentiment,
                        importance_score = EXCLUDED.importance_score,
                        analyzed_at = NOW()
                    RETURNING id
                """, (
                    trend_id,
                    analysis.get('summary'),
                    analysis.get('category'),
                    analysis.get('problems', []),
                    analysis.get('keywords', []),
                    analysis.get('sentiment'),
                    analysis.get('importance_score')
                ))

                analysis_id = cur.fetchone()[0]
                conn.commit()
                return analysis_id

    def save_solutions(self, analyzed_trend_id: int, solutions: List[Dict]) -> int:
        """
        솔루션 아이디어 저장

        Args:
            analyzed_trend_id: 분석된 트렌드 ID
            solutions: 솔루션 리스트

        Returns:
            저장된 솔루션 개수
        """
        saved_count = 0

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for solution in solutions:
                    try:
                        cur.execute("""
                            INSERT INTO solutions (
                                analyzed_trend_id, title, description,
                                feasibility, estimated_effort,
                                target_audience, tech_stack
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            analyzed_trend_id,
                            solution.get('title'),
                            solution.get('description'),
                            solution.get('feasibility'),
                            solution.get('estimated_effort'),
                            solution.get('target_audience'),
                            solution.get('tech_stack', [])
                        ))

                        saved_count += 1

                    except Exception as e:
                        logger.warning(f"솔루션 저장 실패: {str(e)}")
                        continue

                conn.commit()

        return saved_count

    def get_today_stats(self) -> Dict:
        """오늘의 통계 조회"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT t.id) as total_trends,
                        COUNT(DISTINCT at.id) as analyzed_trends,
                        COUNT(DISTINCT sol.id) as total_solutions,
                        AVG(at.importance_score) as avg_importance
                    FROM trends t
                    LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                    LEFT JOIN solutions sol ON at.id = sol.analyzed_trend_id
                    WHERE DATE(t.collected_at) = CURRENT_DATE
                """)

                stats = cur.fetchone()
                return dict(stats) if stats else {}

    def get_source_stats(self, source_name: str) -> Dict:
        """특정 소스의 통계 조회"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT t.id) as total_trends,
                        COUNT(DISTINCT at.id) as analyzed_trends,
                        COUNT(DISTINCT sol.id) as total_solutions,
                        AVG(at.importance_score) as avg_importance
                    FROM trends t
                    JOIN sources s ON t.source_id = s.id
                    LEFT JOIN analyzed_trends at ON t.id = at.trend_id
                    LEFT JOIN solutions sol ON at.id = sol.analyzed_trend_id
                    WHERE s.name = %s
                """, (source_name,))

                stats = cur.fetchone()
                return dict(stats) if stats else {}


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    db = DatabaseManager()

    logger.info("=" * 60)
    logger.info("데이터베이스 연결 테스트")
    logger.info("=" * 60)

    # 소스 ID 조회
    source_id = db.get_source_id('github_trending')
    logger.info(f"github_trending source_id: {source_id}")

    # 오늘의 통계
    stats = db.get_today_stats()
    logger.info("오늘의 통계:")
    logger.info(f"  - 수집된 트렌드: {stats.get('total_trends', 0)}개")
    logger.info(f"  - 분석 완료: {stats.get('analyzed_trends', 0)}개")
    logger.info(f"  - 생성된 솔루션: {stats.get('total_solutions', 0)}개")
