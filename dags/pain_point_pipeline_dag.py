"""
Pain Point 수집 및 분석 통합 파이프라인 DAG
Reddit, Product Hunt, Indie Hackers에서 Pain Point를 수집하고
Claude API + RAG로 분석하여 SaaS 아이디어 생성
"""
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

# DAG 경로를 Python 경로에 추가
dag_folder = Path(__file__).parent
sys.path.insert(0, str(dag_folder))

from collectors.reddit_collector import collect_all_subreddits, TARGET_SUBREDDITS
from collectors.indie_hackers_collector import collect_all_indie_hackers
from collectors.producthunt import scrape_producthunt
from database.pain_point_db_manager import PainPointDBManager
from ai_analysis.rag_engine import RAGEngine
from ai_analysis.claude_analyzer import ClaudeAnalyzer
from ai_analysis.market_validator import MarketValidator
from ai_analysis.multi_agent_system import AgentCoordinator
from config import CRAWLING_CONFIG, AI_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


def collect_reddit_task(**context):
    """Reddit Pain Point 수집 태스크"""
    logger.info("=" * 60)
    logger.info("Reddit Pain Point 수집 시작")
    logger.info("=" * 60)

    try:
        # Reddit 수집
        contents = collect_all_subreddits(subreddits=TARGET_SUBREDDITS)

        if not contents:
            logger.warning("수집된 Reddit 콘텐츠가 없습니다.")
            context['task_instance'].xcom_push(key='reddit_count', value=0)
            return

        # DB 저장
        db = PainPointDBManager()
        saved_count = 0

        for content in contents:
            # 소스 이름 결정 (subreddit별로)
            subreddit = content['metadata'].get('subreddit', 'unknown')
            source_name = f"reddit_{subreddit.lower()}"

            content_id = db.save_raw_content(
                source_name=source_name,
                content_type=content['content_type'],
                title=content['title'],
                body=content['body'],
                author=content['author'],
                url=content['url'],
                external_id=content['external_id'],
                metadata=content['metadata']
            )

            if content_id:
                saved_count += 1

        logger.info(f"Reddit 수집 완료: {saved_count}개 저장")
        context['task_instance'].xcom_push(key='reddit_count', value=saved_count)

    except Exception as e:
        logger.error(f"Reddit 수집 실패: {str(e)}")
        raise


def collect_indie_hackers_task(**context):
    """Indie Hackers 수집 태스크"""
    logger.info("=" * 60)
    logger.info("Indie Hackers 수집 시작")
    logger.info("=" * 60)

    try:
        # Indie Hackers 수집
        forum_limit = CRAWLING_CONFIG.get('indie_hackers_limit', 20)
        contents = collect_all_indie_hackers(
            forum_limit=int(forum_limit * 0.7),  # 70%는 포럼
            story_limit=int(forum_limit * 0.3)   # 30%는 인터뷰
        )

        if not contents:
            logger.warning("수집된 Indie Hackers 콘텐츠가 없습니다.")
            context['task_instance'].xcom_push(key='indie_hackers_count', value=0)
            return

        # DB 저장
        db = PainPointDBManager()
        saved_count = db.save_raw_contents_batch('indie_hackers', contents)

        logger.info(f"Indie Hackers 수집 완료: {saved_count}개 저장")
        context['task_instance'].xcom_push(key='indie_hackers_count', value=saved_count)

    except Exception as e:
        logger.error(f"Indie Hackers 수집 실패: {str(e)}")
        # Indie Hackers는 실패해도 전체 파이프라인 중단하지 않음
        logger.warning("Indie Hackers 수집 실패, 계속 진행")
        context['task_instance'].xcom_push(key='indie_hackers_count', value=0)


def collect_producthunt_task(**context):
    """Product Hunt 수집 태스크"""
    logger.info("=" * 60)
    logger.info("Product Hunt 수집 시작")
    logger.info("=" * 60)

    try:
        # Product Hunt 수집
        limit = CRAWLING_CONFIG.get('producthunt_limit', 20)
        products = scrape_producthunt(limit=limit)

        if not products:
            logger.warning("수집된 Product Hunt 제품이 없습니다.")
            context['task_instance'].xcom_push(key='producthunt_count', value=0)
            return

        # 형식 변환
        contents = []
        for product in products:
            content = {
                'content_type': 'product',
                'title': product['title'],
                'body': product['description'],
                'author': '',  # Product Hunt에는 author 없음
                'url': product['url'],
                'external_id': product['url'].split('/')[-1],  # URL에서 ID 추출
                'metadata': product['metadata']
            }
            contents.append(content)

        # DB 저장
        db = PainPointDBManager()
        saved_count = db.save_raw_contents_batch('product_hunt', contents)

        logger.info(f"Product Hunt 수집 완료: {saved_count}개 저장")
        context['task_instance'].xcom_push(key='producthunt_count', value=saved_count)

    except Exception as e:
        logger.error(f"Product Hunt 수집 실패: {str(e)}")
        raise


def analyze_pain_points_task(**context):
    """Pain Point 분석 태스크 (Claude API + RAG + Multi-Agent)"""
    logger.info("=" * 60)
    logger.info("Pain Point 분석 시작")
    use_multi_agent = AI_CONFIG.get('use_multi_agent', True)
    logger.info(f"Multi-Agent Mode: {'ENABLED' if use_multi_agent else 'DISABLED'}")
    logger.info("=" * 60)

    try:
        db = PainPointDBManager()
        rag = RAGEngine()

        # Multi-agent 또는 단일 analyzer 선택
        if use_multi_agent:
            coordinator = AgentCoordinator()
        else:
            analyzer = ClaudeAnalyzer()

        # 미분석 콘텐츠 가져오기
        analyze_limit = CRAWLING_CONFIG.get('analyze_limit', 10)
        unanalyzed = db.get_unanalyzed_contents(limit=analyze_limit)

        if not unanalyzed:
            logger.warning("분석할 콘텐츠가 없습니다.")
            context['task_instance'].xcom_push(key='analyzed_count', value=0)
            return

        logger.info(f"분석 대상: {len(unanalyzed)}개 콘텐츠")

        analyzed_count = 0

        for content in unanalyzed:
            logger.info("=" * 60)
            logger.info(f"분석 중: {content['title'][:50]}...")
            logger.info("=" * 60)

            # 1. RAG로 유사 Pain Point 검색
            query_text = f"{content['title']}\n\n{content['body']}"
            similar_pain_points = rag.search_similar_pain_points(
                query_text,
                n_results=5,
                min_similarity=0.6
            )

            # 2. Pain Point 추출 (Multi-agent 또는 단일 analyzer)
            if use_multi_agent:
                pain_point = coordinator.analyze_with_agents(
                    content=content,
                    similar_contexts=similar_pain_points
                )
            else:
                pain_point = analyzer.extract_pain_point(
                    content=content,
                    similar_pain_points=similar_pain_points
                )

            if not pain_point:
                logger.info("Pain Point 없음, 스킵")
                continue

            # 3. Embedding 생성
            try:
                problem_text = f"{pain_point['problem_statement']}\n\n{pain_point['problem_detail']}"
                embedding = rag.create_embedding(problem_text)
            except Exception as e:
                logger.warning(f"Embedding 생성 실패: {str(e)}, embedding 없이 저장")
                embedding = None

            # 4. DB에 Pain Point 저장
            pain_point_id = db.save_pain_point(
                content_id=content['id'],
                pain_point_data=pain_point,
                embedding=embedding
            )

            if not pain_point_id:
                logger.warning("Pain Point 저장 실패")
                continue

            # 5. ChromaDB에도 저장
            if embedding:
                try:
                    rag.add_pain_point(
                        pain_point_id=pain_point_id,
                        problem_statement=pain_point['problem_statement'],
                        problem_detail=pain_point['problem_detail'],
                        metadata={
                            'affected_users': pain_point['affected_users'],
                            'severity': pain_point['severity'],
                            'category': pain_point['category']
                        }
                    )
                except Exception as e:
                    logger.warning(f"ChromaDB 저장 실패: {str(e)}")

            analyzed_count += 1

        logger.info("=" * 60)
        logger.info(f"Pain Point 분석 완료: {analyzed_count}개")
        logger.info("=" * 60)

        context['task_instance'].xcom_push(key='analyzed_count', value=analyzed_count)

    except Exception as e:
        logger.error(f"Pain Point 분석 실패: {str(e)}")
        raise


def generate_ideas_task(**context):
    """SaaS 아이디어 생성 태스크"""
    logger.info("=" * 60)
    logger.info("SaaS 아이디어 생성 시작")
    logger.info("=" * 60)

    try:
        db = PainPointDBManager()
        analyzer = ClaudeAnalyzer()

        # Pain Point ID 가져오기 (최근 분석된 것들)
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT pp.id, pp.problem_statement, pp.problem_detail,
                           pp.affected_users, pp.severity, pp.market_size,
                           pp.existing_solutions, pp.solution_gaps
                    FROM pain_points pp
                    LEFT JOIN saas_ideas si ON pp.id = si.pain_point_id
                    WHERE si.id IS NULL
                    ORDER BY pp.analyzed_at DESC
                    LIMIT 10
                """)

                pain_points = cur.fetchall()

        if not pain_points:
            logger.warning("아이디어를 생성할 Pain Point가 없습니다.")
            context['task_instance'].xcom_push(key='ideas_count', value=0)
            return

        logger.info(f"아이디어 생성 대상: {len(pain_points)}개 Pain Point")

        total_ideas = 0

        for pp in pain_points:
            pain_point_id, problem_statement, problem_detail, affected_users, severity, market_size, existing_solutions, solution_gaps = pp

            logger.info(f"\n아이디어 생성 중: {problem_statement[:50]}...")

            # Pain Point 데이터 구성
            pain_point_data = {
                'problem_statement': problem_statement,
                'problem_detail': problem_detail,
                'affected_users': affected_users,
                'severity': severity,
                'market_size': market_size,
                'existing_solutions': existing_solutions or [],
                'solution_gaps': solution_gaps
            }

            # SaaS 아이디어 생성
            ideas = analyzer.generate_saas_ideas(
                pain_point=pain_point_data,
                similar_products=existing_solutions
            )

            if not ideas:
                logger.warning("아이디어 생성 실패")
                continue

            # DB에 저장
            saved_count = db.save_saas_ideas_batch(pain_point_id, ideas)
            total_ideas += saved_count

        logger.info("=" * 60)
        logger.info(f"SaaS 아이디어 생성 완료: {total_ideas}개")
        logger.info("=" * 60)

        context['task_instance'].xcom_push(key='ideas_count', value=total_ideas)

    except Exception as e:
        logger.error(f"아이디어 생성 실패: {str(e)}")
        raise


def validate_market_task(**context):
    """시장 검증 태스크 (Google Trends + 경쟁사 분석)"""
    logger.info("=" * 60)
    logger.info("시장 검증 시작")
    logger.info("=" * 60)

    try:
        db = PainPointDBManager()
        validator = MarketValidator()

        # 미검증 아이디어 가져오기
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT si.id, si.title, si.problem_statement, si.keywords,
                           si.target_audience, si.overall_score
                    FROM saas_ideas si
                    LEFT JOIN market_validation mv ON si.id = mv.idea_id
                    WHERE mv.id IS NULL
                    ORDER BY si.created_at DESC
                    LIMIT 5
                """)

                ideas = cur.fetchall()

        if not ideas:
            logger.warning("검증할 아이디어가 없습니다.")
            context['task_instance'].xcom_push(key='validated_count', value=0)
            return

        logger.info(f"시장 검증 대상: {len(ideas)}개 아이디어")

        validated_count = 0

        for idea in ideas:
            idea_id, title, problem_statement, keywords, target_audience, overall_score = idea

            logger.info(f"\n검증 중: {title}")

            # 아이디어 데이터 구성
            idea_data = {
                'title': title,
                'problem_statement': problem_statement,
                'keywords': keywords or [],
                'target_audience': target_audience
            }

            # 시장 검증 수행
            validation_result = validator.validate_idea(idea_data)

            # DB에 저장
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO market_validation (
                            idea_id, search_volume_score, trend_direction,
                            competitor_count, competitors, saturation_score,
                            market_status, validation_score, recommendation,
                            validated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                        )
                    """, (
                        idea_id,
                        validation_result['search_volume_score'],
                        validation_result['trend_direction'],
                        validation_result['competitor_count'],
                        validation_result['competitors'],
                        validation_result['saturation_score'],
                        validation_result['market_status'],
                        validation_result['validation_score'],
                        validation_result['recommendation']
                    ))
                    conn.commit()

            validated_count += 1
            logger.info(f"  ✓ 검증 점수: {validation_result['validation_score']}/10")
            logger.info(f"  ✓ 시장 상태: {validation_result['market_status']}")

        logger.info("=" * 60)
        logger.info(f"시장 검증 완료: {validated_count}개")
        logger.info("=" * 60)

        context['task_instance'].xcom_push(key='validated_count', value=validated_count)

    except Exception as e:
        logger.error(f"시장 검증 실패: {str(e)}")
        # 시장 검증 실패해도 전체 파이프라인은 계속 진행
        logger.warning("시장 검증 실패, 계속 진행")
        context['task_instance'].xcom_push(key='validated_count', value=0)


def print_summary_task(**context):
    """일일 요약 출력 태스크"""
    logger.info("=" * 60)
    logger.info("Pain Point Finder 일일 요약")
    logger.info("=" * 60)

    try:
        db = PainPointDBManager()
        stats = db.get_today_stats()

        logger.info("\n오늘의 통계:")
        logger.info(f"  - 수집된 콘텐츠: {stats.get('total_contents', 0)}개")
        logger.info(f"  - 분석된 Pain Points: {stats.get('total_pain_points', 0)}개")
        logger.info(f"  - 생성된 SaaS 아이디어: {stats.get('total_ideas', 0)}개")

        avg_confidence = stats.get('avg_confidence')
        if avg_confidence:
            logger.info(f"  - 평균 신뢰도: {float(avg_confidence):.2f}")

        avg_score = stats.get('avg_idea_score')
        if avg_score:
            logger.info(f"  - 평균 아이디어 점수: {float(avg_score):.1f}/10")

        # XCom에서 이번 실행 결과 가져오기
        ti = context['task_instance']
        reddit = ti.xcom_pull(task_ids='collect_reddit', key='reddit_count') or 0
        indie = ti.xcom_pull(task_ids='collect_indie_hackers', key='indie_hackers_count') or 0
        ph = ti.xcom_pull(task_ids='collect_producthunt', key='producthunt_count') or 0
        analyzed = ti.xcom_pull(task_ids='analyze_pain_points', key='analyzed_count') or 0
        ideas = ti.xcom_pull(task_ids='generate_ideas', key='ideas_count') or 0
        validated = ti.xcom_pull(task_ids='validate_market', key='validated_count') or 0

        logger.info("\n이번 실행 결과:")
        logger.info(f"  - Reddit: {reddit}개")
        logger.info(f"  - Indie Hackers: {indie}개")
        logger.info(f"  - Product Hunt: {ph}개")
        logger.info(f"  - 분석: {analyzed}개")
        logger.info(f"  - 아이디어: {ideas}개")
        logger.info(f"  - 시장 검증: {validated}개")

        # Top 아이디어
        top_ideas = db.get_top_ideas(limit=3)
        if top_ideas:
            logger.info("\nTop 3 아이디어:")
            for i, idea in enumerate(top_ideas, 1):
                logger.info(f"  [{i}] {idea['title']} (Score: {idea['overall_score']}/10)")
                logger.info(f"      Problem: {idea['problem_statement'][:50]}...")

        logger.info("\nPain Point Finder 실행 완료!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"요약 출력 실패: {str(e)}")
        raise


# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'pain_point_finder_pipeline',
    default_args=default_args,
    description='Pain Point 수집 및 SaaS 아이디어 생성 파이프라인',
    schedule='0 9 * * *',  # 매일 오전 9시 실행
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['pain-point', 'saas', 'claude', 'rag'],
) as dag:

    # Task 1: Reddit 수집
    reddit_task = PythonOperator(
        task_id='collect_reddit',
        python_callable=collect_reddit_task,
    )

    # Task 2: Indie Hackers 수집
    indie_task = PythonOperator(
        task_id='collect_indie_hackers',
        python_callable=collect_indie_hackers_task,
    )

    # Task 3: Product Hunt 수집
    ph_task = PythonOperator(
        task_id='collect_producthunt',
        python_callable=collect_producthunt_task,
    )

    # Task 4: Pain Point 분석 (Claude API + RAG)
    analyze_task = PythonOperator(
        task_id='analyze_pain_points',
        python_callable=analyze_pain_points_task,
    )

    # Task 5: SaaS 아이디어 생성
    ideas_task = PythonOperator(
        task_id='generate_ideas',
        python_callable=generate_ideas_task,
    )

    # Task 6: 시장 검증 (Google Trends + 경쟁사 분석)
    validation_task = PythonOperator(
        task_id='validate_market',
        python_callable=validate_market_task,
    )

    # Task 7: 일일 요약 출력
    summary_task = PythonOperator(
        task_id='print_summary',
        python_callable=print_summary_task,
    )

    # Task 의존성 정의
    # 모든 수집 태스크를 병렬로 실행 → 분석 → 아이디어 생성 → 시장 검증 → 요약
    [reddit_task, indie_task, ph_task] >> analyze_task >> ideas_task >> validation_task >> summary_task
