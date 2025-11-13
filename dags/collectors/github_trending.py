"""
GitHub Trending - GitHub Search API 사용
"""
import requests
from typing import List, Dict
from datetime import datetime, timedelta
import logging
import sys
import os
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)

# GitHub Token (환경변수에서 가져오기)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')


def scrape_github_trending(language: str = "", limit: int = None) -> List[Dict]:
    """
    GitHub Search API를 사용하여 트렌딩 레포지토리 검색

    최근 7일간 생성된 레포지토리 중 별(stars)이 많은 순서로 정렬

    Args:
        language: 프로그래밍 언어 필터 (예: 'python', 'javascript', '')
        limit: 가져올 최대 개수 (None이면 config의 기본값 사용)

    Returns:
        List of trending repositories

    Raises:
        ValueError: GitHub Token이 설정되지 않은 경우
    """
    if limit is None:
        limit = CRAWLING_CONFIG.get('github_trending_limit', 25)

    if not GITHUB_TOKEN:
        error_msg = (
            "GitHub Token이 설정되지 않았습니다.\n"
            "환경변수 GITHUB_TOKEN을 설정해주세요.\n"
            "Token 발급: https://github.com/settings/tokens"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("GitHub Search API를 사용하여 트렌딩 레포지토리 검색 시작")
    return fetch_from_api(language, limit)


def fetch_from_api(language: str, limit: int) -> List[Dict]:
    """
    GitHub Search API에서 데이터 가져오기

    Args:
        language: 프로그래밍 언어 필터
        limit: 가져올 최대 개수

    Returns:
        List of trending repositories

    Raises:
        requests.RequestException: API 요청 실패 시
    """
    # 최근 7일간 생성된 레포지토리 검색
    date_7_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 검색 쿼리 생성
    query = f"created:>{date_7_days_ago}"
    if language:
        query += f" language:{language}"

    url = "https://api.github.com/search/repositories"
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': min(limit, 100)  # GitHub API 최대 100
    }

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    try:
        logger.info(f"GitHub API 호출 중... (query: {query})")
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=CRAWLING_CONFIG['request_timeout']
        )
        response.raise_for_status()

        data = response.json()

        # Rate Limit 정보 로깅
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
        logger.info(f"API Rate Limit 남음: {rate_limit_remaining}")

        items = data.get('items', [])

        trends = []
        for idx, repo in enumerate(items[:limit]):
            trend = {
                'title': repo.get('full_name', ''),
                'description': repo.get('description', '') or '',
                'url': repo.get('html_url', ''),
                'category': repo.get('language', 'Unknown') or 'Unknown',
                'rank': idx + 1,
                'metadata': {
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'watchers': repo.get('watchers_count', 0),
                    'open_issues': repo.get('open_issues_count', 0),
                    'language': repo.get('language', 'Unknown') or 'Unknown',
                    'created_at': repo.get('created_at', ''),
                    'updated_at': repo.get('updated_at', ''),
                }
            }
            trends.append(trend)
            logger.debug(f"[{idx + 1}] {trend['title']} - Stars: {trend['metadata']['stars']}")

        logger.info(f"API에서 {len(trends)}개 레포지토리 수집 완료")
        return trends

    except requests.RequestException as e:
        error_msg = f"GitHub API 요청 실패: {str(e)}"
        logger.error(error_msg)

        # 응답이 있으면 에러 메시지 출력
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                logger.error(f"API 에러 응답: {error_data}")
            except:
                logger.error(f"API 응답 코드: {e.response.status_code}")

        raise
    except Exception as e:
        error_msg = f"GitHub 데이터 처리 중 오류: {str(e)}"
        logger.error(error_msg)
        raise


def test_scraper():
    """크롤러 테스트"""
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("=" * 60)
    logger.info("GitHub Trending API 테스트")
    logger.info("=" * 60)

    try:
        trends = scrape_github_trending(limit=10)

        logger.info(f"\n수집 결과: {len(trends)}개")
        for trend in trends:
            logger.info(f"\n#{trend['rank']} {trend['title']}")
            logger.info(f"설명: {trend['description'][:100]}...")
            logger.info(f"언어: {trend['category']}")
            logger.info(f"URL: {trend['url']}")
            logger.info(f"별: {trend['metadata']['stars']}, 포크: {trend['metadata']['forks']}")

        return trends
    except ValueError as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        logger.error("\n.env 파일에 GITHUB_TOKEN을 추가하거나")
        logger.error("환경변수로 설정해주세요:")
        logger.error("  export GITHUB_TOKEN='your_token_here'")
        return []
    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        return []


if __name__ == "__main__":
    test_scraper()
