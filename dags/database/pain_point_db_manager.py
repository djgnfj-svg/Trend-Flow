"""
Pain Point Finder Database Manager
새로운 스키마 (raw_contents, pain_points, saas_ideas)에 맞춘 DB 관리자
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


class PainPointDBManager:
    """Pain Point Finder용 PostgreSQL 데이터베이스 관리 클래스"""

    def __init__(self, **kwargs):
        """
        데이터베이스 연결 초기화

        Args:
            **kwargs: 데이터베이스 연결 파라미터 (선택사항)
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

    # ==========================================
    # Raw Contents (원본 데이터) 관리
    # ==========================================

    def save_raw_content(
        self,
        source_name: str,
        content_type: str,
        title: str,
        body: str,
        author: str,
        url: str,
        external_id: str,
        metadata: Dict
    ) -> Optional[int]:
        """
        원본 콘텐츠 저장

        Args:
            source_name: 소스 이름 (reddit_sideproject, product_hunt, etc.)
            content_type: 콘텐츠 타입 (post, comment, product)
            title: 제목
            body: 본문
            author: 작성자
            url: URL
            external_id: 소스별 고유 ID
            metadata: 추가 메타데이터

        Returns:
            저장된 콘텐츠 ID, 중복이면 None
        """
        source_id = self.get_source_id(source_name)
        if not source_id:
            logger.warning(f"Source '{source_name}' not found, skipping")
            return None

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO raw_contents (
                            source_id, content_type, title, body,
                            author, url, external_id, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (source_id, external_id) DO NOTHING
                        RETURNING id
                    """, (
                        source_id, content_type, title, body,
                        author, url, external_id, Json(metadata)
                    ))

                    result = cur.fetchone()
                    conn.commit()

                    if result:
                        content_id = result[0]
                        logger.debug(f"원본 콘텐츠 저장: ID={content_id}, {title[:50]}...")
                        return content_id
                    else:
                        logger.debug(f"중복 스킵: {title[:50]}...")
                        return None

                except Exception as e:
                    logger.error(f"원본 콘텐츠 저장 실패: {str(e)}")
                    conn.rollback()
                    return None

    def save_raw_contents_batch(
        self,
        source_name: str,
        contents: List[Dict]
    ) -> int:
        """
        원본 콘텐츠 배치 저장

        Args:
            source_name: 소스 이름
            contents: 콘텐츠 리스트 (각 딕셔너리는 content_type, title, body 등 포함)

        Returns:
            저장된 개수
        """
        saved_count = 0

        for content in contents:
            content_id = self.save_raw_content(
                source_name=source_name,
                content_type=content.get('content_type', 'post'),
                title=content.get('title', ''),
                body=content.get('body', ''),
                author=content.get('author', ''),
                url=content.get('url', ''),
                external_id=content.get('external_id', ''),
                metadata=content.get('metadata', {})
            )

            if content_id:
                saved_count += 1

        logger.info(f"{source_name}: {saved_count}/{len(contents)}개 저장")
        return saved_count

    def get_unanalyzed_contents(
        self,
        limit: Optional[int] = None,
        source_name: Optional[str] = None
    ) -> List[Dict]:
        """
        아직 분석되지 않은 원본 콘텐츠 가져오기

        Args:
            limit: 가져올 최대 개수
            source_name: 특정 소스만 필터링

        Returns:
            미분석 콘텐츠 리스트
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT rc.id, rc.content_type, rc.title, rc.body,
                           rc.author, rc.url, rc.external_id, rc.metadata,
                           s.name as source_name
                    FROM raw_contents rc
                    JOIN sources s ON rc.source_id = s.id
                    LEFT JOIN pain_points pp ON rc.id = pp.content_id
                    WHERE pp.id IS NULL
                """

                params = []
                if source_name:
                    query += " AND s.name = %s"
                    params.append(source_name)

                query += " ORDER BY rc.collected_at DESC"

                if limit:
                    query += " LIMIT %s"
                    params.append(limit)

                cur.execute(query, params)
                contents = cur.fetchall()
                return [dict(content) for content in contents]

    # ==========================================
    # Pain Points 관리
    # ==========================================

    def save_pain_point(
        self,
        content_id: int,
        pain_point_data: Dict,
        embedding: Optional[List[float]] = None
    ) -> Optional[int]:
        """
        Pain Point 저장

        Args:
            content_id: raw_contents 테이블의 ID
            pain_point_data: Pain Point 데이터 (Claude API 출력)
            embedding: Vector embedding (선택)

        Returns:
            저장된 Pain Point ID
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    # embedding이 있으면 포함, 없으면 제외
                    if embedding:
                        cur.execute("""
                            INSERT INTO pain_points (
                                content_id, problem_statement, problem_detail,
                                affected_users, frequency, severity,
                                market_size, willingness_to_pay,
                                existing_solutions, solution_gaps,
                                keywords, category, confidence_score,
                                embedding
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (content_id) DO UPDATE SET
                                problem_statement = EXCLUDED.problem_statement,
                                problem_detail = EXCLUDED.problem_detail,
                                affected_users = EXCLUDED.affected_users,
                                frequency = EXCLUDED.frequency,
                                severity = EXCLUDED.severity,
                                market_size = EXCLUDED.market_size,
                                willingness_to_pay = EXCLUDED.willingness_to_pay,
                                existing_solutions = EXCLUDED.existing_solutions,
                                solution_gaps = EXCLUDED.solution_gaps,
                                keywords = EXCLUDED.keywords,
                                category = EXCLUDED.category,
                                confidence_score = EXCLUDED.confidence_score,
                                embedding = EXCLUDED.embedding,
                                analyzed_at = NOW()
                            RETURNING id
                        """, (
                            content_id,
                            pain_point_data.get('problem_statement'),
                            pain_point_data.get('problem_detail'),
                            pain_point_data.get('affected_users'),
                            pain_point_data.get('frequency'),
                            pain_point_data.get('severity'),
                            pain_point_data.get('market_size'),
                            pain_point_data.get('willingness_to_pay'),
                            pain_point_data.get('existing_solutions', []),
                            pain_point_data.get('solution_gaps'),
                            pain_point_data.get('keywords', []),
                            pain_point_data.get('category'),
                            pain_point_data.get('confidence_score'),
                            embedding
                        ))
                    else:
                        # embedding 없이 저장
                        cur.execute("""
                            INSERT INTO pain_points (
                                content_id, problem_statement, problem_detail,
                                affected_users, frequency, severity,
                                market_size, willingness_to_pay,
                                existing_solutions, solution_gaps,
                                keywords, category, confidence_score
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (content_id) DO UPDATE SET
                                problem_statement = EXCLUDED.problem_statement,
                                problem_detail = EXCLUDED.problem_detail,
                                affected_users = EXCLUDED.affected_users,
                                frequency = EXCLUDED.frequency,
                                severity = EXCLUDED.severity,
                                market_size = EXCLUDED.market_size,
                                willingness_to_pay = EXCLUDED.willingness_to_pay,
                                existing_solutions = EXCLUDED.existing_solutions,
                                solution_gaps = EXCLUDED.solution_gaps,
                                keywords = EXCLUDED.keywords,
                                category = EXCLUDED.category,
                                confidence_score = EXCLUDED.confidence_score,
                                analyzed_at = NOW()
                            RETURNING id
                        """, (
                            content_id,
                            pain_point_data.get('problem_statement'),
                            pain_point_data.get('problem_detail'),
                            pain_point_data.get('affected_users'),
                            pain_point_data.get('frequency'),
                            pain_point_data.get('severity'),
                            pain_point_data.get('market_size'),
                            pain_point_data.get('willingness_to_pay'),
                            pain_point_data.get('existing_solutions', []),
                            pain_point_data.get('solution_gaps'),
                            pain_point_data.get('keywords', []),
                            pain_point_data.get('category'),
                            pain_point_data.get('confidence_score')
                        ))

                    pain_point_id = cur.fetchone()[0]
                    conn.commit()

                    logger.info(f"Pain Point 저장 완료: ID={pain_point_id}")
                    return pain_point_id

                except Exception as e:
                    logger.error(f"Pain Point 저장 실패: {str(e)}")
                    conn.rollback()
                    return None

    # ==========================================
    # SaaS Ideas 관리
    # ==========================================

    def save_saas_idea(
        self,
        pain_point_id: int,
        idea_data: Dict
    ) -> Optional[int]:
        """
        SaaS 아이디어 저장

        Args:
            pain_point_id: pain_points 테이블의 ID
            idea_data: 아이디어 데이터 (Claude API 출력)

        Returns:
            저장된 아이디어 ID
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO saas_ideas (
                            pain_point_id, title, tagline, description,
                            business_model, pricing_model, estimated_monthly_revenue,
                            tech_stack, complexity, estimated_dev_time,
                            mvp_features, mvp_description,
                            target_audience, go_to_market_strategy,
                            competition_level, differentiation,
                            feasibility_score, market_score, overall_score,
                            tags, similar_products
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        pain_point_id,
                        idea_data.get('title'),
                        idea_data.get('tagline'),
                        idea_data.get('description'),
                        idea_data.get('business_model'),
                        idea_data.get('pricing_model'),
                        idea_data.get('estimated_monthly_revenue'),
                        idea_data.get('tech_stack', []),
                        idea_data.get('complexity'),
                        idea_data.get('estimated_dev_time'),
                        idea_data.get('mvp_features', []),
                        idea_data.get('mvp_description'),
                        idea_data.get('target_audience'),
                        idea_data.get('go_to_market_strategy'),
                        idea_data.get('competition_level'),
                        idea_data.get('differentiation'),
                        idea_data.get('feasibility_score'),
                        idea_data.get('market_score'),
                        idea_data.get('overall_score'),
                        idea_data.get('tags', []),
                        idea_data.get('similar_products', [])
                    ))

                    idea_id = cur.fetchone()[0]
                    conn.commit()

                    logger.info(f"SaaS 아이디어 저장 완료: ID={idea_id}, {idea_data.get('title')}")
                    return idea_id

                except Exception as e:
                    logger.error(f"SaaS 아이디어 저장 실패: {str(e)}")
                    conn.rollback()
                    return None

    def save_saas_ideas_batch(
        self,
        pain_point_id: int,
        ideas: List[Dict]
    ) -> int:
        """
        SaaS 아이디어 배치 저장

        Args:
            pain_point_id: pain_points 테이블의 ID
            ideas: 아이디어 리스트

        Returns:
            저장된 개수
        """
        saved_count = 0

        for idea in ideas:
            idea_id = self.save_saas_idea(pain_point_id, idea)
            if idea_id:
                saved_count += 1

        logger.info(f"{saved_count}/{len(ideas)}개 아이디어 저장 완료")
        return saved_count

    # ==========================================
    # 통계 및 조회
    # ==========================================

    def get_today_stats(self) -> Dict:
        """오늘의 통계 조회"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT rc.id) as total_contents,
                        COUNT(DISTINCT pp.id) as total_pain_points,
                        COUNT(DISTINCT si.id) as total_ideas,
                        AVG(pp.confidence_score) as avg_confidence,
                        AVG(si.overall_score) as avg_idea_score
                    FROM raw_contents rc
                    LEFT JOIN pain_points pp ON rc.id = pp.content_id
                    LEFT JOIN saas_ideas si ON pp.id = si.pain_point_id
                    WHERE DATE(rc.collected_at) = CURRENT_DATE
                """)

                stats = cur.fetchone()
                return dict(stats) if stats else {}

    def get_source_stats(self, source_name: str) -> Dict:
        """특정 소스의 통계 조회"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT rc.id) as total_contents,
                        COUNT(DISTINCT pp.id) as total_pain_points,
                        COUNT(DISTINCT si.id) as total_ideas,
                        AVG(pp.confidence_score) as avg_confidence,
                        AVG(si.overall_score) as avg_idea_score
                    FROM raw_contents rc
                    JOIN sources s ON rc.source_id = s.id
                    LEFT JOIN pain_points pp ON rc.id = pp.content_id
                    LEFT JOIN saas_ideas si ON pp.id = si.pain_point_id
                    WHERE s.name = %s
                """, (source_name,))

                stats = cur.fetchone()
                return dict(stats) if stats else {}

    def get_top_ideas(self, limit: int = 10) -> List[Dict]:
        """최고 점수 아이디어 조회"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        si.*,
                        pp.problem_statement,
                        pp.severity,
                        pp.affected_users,
                        s.name as source_name
                    FROM saas_ideas si
                    JOIN pain_points pp ON si.pain_point_id = pp.id
                    JOIN raw_contents rc ON pp.content_id = rc.id
                    JOIN sources s ON rc.source_id = s.id
                    ORDER BY si.overall_score DESC, si.created_at DESC
                    LIMIT %s
                """, (limit,))

                ideas = cur.fetchall()
                return [dict(idea) for idea in ideas]


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db = PainPointDBManager()

    logger.info("=" * 60)
    logger.info("Pain Point DB Manager 테스트")
    logger.info("=" * 60)

    # 소스 ID 조회
    source_id = db.get_source_id('reddit_sideproject')
    logger.info(f"reddit_sideproject source_id: {source_id}")

    # 오늘의 통계
    stats = db.get_today_stats()
    logger.info("\n오늘의 통계:")
    logger.info(f"  - 수집된 콘텐츠: {stats.get('total_contents', 0)}개")
    logger.info(f"  - Pain Points: {stats.get('total_pain_points', 0)}개")
    logger.info(f"  - SaaS 아이디어: {stats.get('total_ideas', 0)}개")

    # Top 아이디어
    top_ideas = db.get_top_ideas(limit=5)
    logger.info(f"\nTop {len(top_ideas)}개 아이디어:")
    for i, idea in enumerate(top_ideas, 1):
        logger.info(f"  [{i}] {idea['title']} (Score: {idea['overall_score']}/10)")
