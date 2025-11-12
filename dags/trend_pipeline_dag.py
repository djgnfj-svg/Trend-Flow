"""
트렌드 수집 및 분석 파이프라인 DAG
매일 자동으로 실행되어 GitHub Trending을 수집하고 AI로 분석
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

from collectors.github_trending import scrape_github_trending
from database.db_manager import DatabaseManager
from ai_analysis.analyzer import TrendAnalyzer
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


def collect_github_trending(**context):
    """GitHub Trending 수집 태스크"""
    logger.info("=" * 60)
    logger.info("GitHub Trending 수집 시작")
    logger.info("=" * 60)

    try:
        # 트렌딩 레포지토리 크롤링
        limit = CRAWLING_CONFIG['github_trending_limit']
        trends = scrape_github_trending(language="", limit=limit)

        if not trends:
            logger.warning("수집된 트렌드가 없습니다.")
            return

        # 데이터베이스에 저장
        db = DatabaseManager()
        saved_count = db.save_trends('github_trending', trends)

        logger.info(f"GitHub Trending 수집 완료: {saved_count}개 저장")

        # XCom으로 결과 전달
        context['task_instance'].xcom_push(key='collected_count', value=saved_count)

    except Exception as e:
        logger.error(f"수집 실패: {str(e)}")
        raise


def analyze_trends(**context):
    """수집된 트렌드 AI 분석 태스크"""
    logger.info("=" * 60)
    logger.info("트렌드 AI 분석 시작")
    logger.info("=" * 60)

    try:
        db = DatabaseManager()
        analyzer = TrendAnalyzer()

        # 분석되지 않은 트렌드 가져오기
        analyze_limit = CRAWLING_CONFIG['analyze_limit']
        unanalyzed = db.get_unanalyzed_trends(limit=analyze_limit)

        if not unanalyzed:
            logger.warning("분석할 트렌드가 없습니다.")
            context['task_instance'].xcom_push(key='analyzed_count', value=0)
            return

        logger.info(f"분석 대상: {len(unanalyzed)}개 트렌드")

        analyzed_count = 0
        solution_count = 0

        for trend in unanalyzed:
            logger.info("=" * 60)
            logger.info(f"분석 중: {trend['title']}")
            logger.info("=" * 60)

            # 1. 트렌드 분석
            analysis = analyzer.analyze_trend(trend)

            if not analysis:
                logger.warning(f"분석 스킵: {trend['title']}")
                continue

            # 2. 분석 결과 저장
            try:
                analyzed_id = db.save_analysis(trend['id'], analysis)
                analyzed_count += 1
                logger.info(f"분석 저장 완료 (ID: {analyzed_id})")

                # 3. 솔루션 생성
                solutions = analyzer.generate_solutions(trend, analysis)

                if solutions:
                    # 4. 솔루션 저장
                    saved_solutions = db.save_solutions(analyzed_id, solutions)
                    solution_count += saved_solutions
                    logger.info(f"솔루션 {saved_solutions}개 저장")

            except Exception as e:
                logger.warning(f"저장 오류 ({trend['title']}): {str(e)}")
                continue

        logger.info("=" * 60)
        logger.info(f"분석 완료: {analyzed_count}개 분석, {solution_count}개 솔루션 생성")
        logger.info("=" * 60)

        # XCom으로 결과 전달
        context['task_instance'].xcom_push(key='analyzed_count', value=analyzed_count)
        context['task_instance'].xcom_push(key='solution_count', value=solution_count)

    except Exception as e:
        logger.error(f"분석 실패: {str(e)}")
        raise


def print_daily_summary(**context):
    """일일 요약 출력 태스크"""
    logger.info("=" * 60)
    logger.info("오늘의 트렌드 수집/분석 요약")
    logger.info("=" * 60)

    try:
        db = DatabaseManager()
        stats = db.get_today_stats()

        logger.info("\n오늘의 통계:")
        logger.info(f"  - 수집된 트렌드: {stats.get('total_trends', 0)}개")
        logger.info(f"  - 분석 완료: {stats.get('analyzed_trends', 0)}개")
        logger.info(f"  - 생성된 솔루션: {stats.get('total_solutions', 0)}개")

        avg_importance = stats.get('avg_importance')
        if avg_importance:
            logger.info(f"  - 평균 중요도: {float(avg_importance):.2f}/10")

        # XCom에서 이번 실행 결과 가져오기
        ti = context['task_instance']
        collected = ti.xcom_pull(task_ids='collect_github_trending', key='collected_count')
        analyzed = ti.xcom_pull(task_ids='analyze_trends', key='analyzed_count')
        solutions = ti.xcom_pull(task_ids='analyze_trends', key='solution_count')

        logger.info("\n이번 실행 결과:")
        logger.info(f"  - 새로 수집: {collected or 0}개")
        logger.info(f"  - 새로 분석: {analyzed or 0}개")
        logger.info(f"  - 새 솔루션: {solutions or 0}개")

        logger.info("\n파이프라인 실행 완료!")
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
    'trend_collection_and_analysis',
    default_args=default_args,
    description='GitHub Trending 수집 및 AI 분석 파이프라인',
    schedule='0 9 * * *',  # 매일 오전 9시 실행
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['trend', 'ai', 'github'],
) as dag:

    # Task 1: GitHub Trending 수집
    collect_task = PythonOperator(
        task_id='collect_github_trending',
        python_callable=collect_github_trending,
    )

    # Task 2: AI 분석 및 솔루션 생성
    analyze_task = PythonOperator(
        task_id='analyze_trends',
        python_callable=analyze_trends,
    )

    # Task 3: 일일 요약 출력
    summary_task = PythonOperator(
        task_id='print_daily_summary',
        python_callable=print_daily_summary,
    )

    # Task 의존성 정의
    collect_task >> analyze_task >> summary_task
