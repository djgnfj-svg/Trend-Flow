"""
Product Hunt 크롤러

Note: Product Hunt는 웹 스크래핑을 차단하므로 공식 API 사용 필수
      API 키 발급: https://api.producthunt.com/v2/docs
      환경변수 PRODUCTHUNT_API_KEY 설정 필요
"""
import requests
from typing import List, Dict
import logging
import sys
from pathlib import Path
import os

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)

# Product Hunt API 키 (환경변수에서 가져오기)
PRODUCTHUNT_API_KEY = os.getenv('PRODUCTHUNT_API_KEY', '')


def scrape_producthunt(limit: int = None) -> List[Dict]:
    """
    Product Hunt에서 인기 제품 수집 (공식 API 사용)

    Args:
        limit: 가져올 최대 개수 (None이면 config의 기본값 사용)

    Returns:
        List of popular products

    Raises:
        ValueError: API 키가 설정되지 않은 경우
    """
    if limit is None:
        limit = CRAWLING_CONFIG.get('producthunt_limit', 20)

    if not PRODUCTHUNT_API_KEY:
        error_msg = (
            "Product Hunt API 키가 설정되지 않았습니다.\n"
            "환경변수 PRODUCTHUNT_API_KEY를 설정해주세요.\n"
            "API 키 발급: https://api.producthunt.com/v2/docs"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Product Hunt API를 사용하여 데이터 수집 시작")
    return fetch_from_api(limit)


def fetch_from_api(limit: int) -> List[Dict]:
    """
    Product Hunt API에서 데이터 가져오기

    Args:
        limit: 가져올 최대 개수

    Returns:
        List of popular products

    Raises:
        requests.RequestException: API 요청 실패 시
    """
    url = "https://api.producthunt.com/v2/api/graphql"

    headers = {
        'Authorization': f'Bearer {PRODUCTHUNT_API_KEY}',
        'Content-Type': 'application/json',
    }

    # GraphQL 쿼리
    query = """
    query {
      posts(first: %d, order: VOTES) {
        edges {
          node {
            id
            name
            tagline
            url
            votesCount
            commentsCount
            topics {
              edges {
                node {
                  name
                }
              }
            }
            featuredAt
          }
        }
      }
    }
    """ % limit

    try:
        logger.info("Product Hunt API 호출 중...")
        response = requests.post(
            url,
            json={'query': query},
            headers=headers,
            timeout=CRAWLING_CONFIG['request_timeout']
        )
        response.raise_for_status()

        data = response.json()

        # API 에러 체크
        if 'errors' in data:
            error_msg = f"Product Hunt API 에러: {data['errors']}"
            logger.error(error_msg)
            raise Exception(error_msg)

        posts = data.get('data', {}).get('posts', {}).get('edges', [])

        trends = []
        for idx, edge in enumerate(posts):
            node = edge.get('node', {})
            topics = [t.get('node', {}).get('name', '') for t in node.get('topics', {}).get('edges', [])]

            trend = {
                'title': node.get('name', ''),
                'description': node.get('tagline', ''),
                'url': node.get('url', ''),
                'category': topics[0] if topics else 'Product',
                'rank': idx + 1,
                'metadata': {
                    'votes': node.get('votesCount', 0),
                    'comments': node.get('commentsCount', 0),
                    'topics': topics,
                    'featured_at': node.get('featuredAt', ''),
                }
            }
            trends.append(trend)
            logger.debug(f"[{idx + 1}] {trend['title']} - Votes: {trend['metadata']['votes']}")

        logger.info(f"API에서 {len(trends)}개 제품 수집 완료")
        return trends

    except requests.RequestException as e:
        error_msg = f"Product Hunt API 요청 실패: {str(e)}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Product Hunt 데이터 처리 중 오류: {str(e)}"
        logger.error(error_msg)
        raise


def test_scraper():
    """크롤러 테스트"""
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("=" * 60)
    logger.info("Product Hunt 크롤러 테스트")
    logger.info("=" * 60)

    try:
        trends = scrape_producthunt(limit=10)

        logger.info(f"\n수집 결과: {len(trends)}개")
        for trend in trends:
            logger.info(f"\n#{trend['rank']} {trend['title']}")
            logger.info(f"설명: {trend['description'][:100]}...")
            logger.info(f"URL: {trend['url']}")
            logger.info(f"투표: {trend['metadata']['votes']}, 댓글: {trend['metadata']['comments']}")

        return trends
    except ValueError as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        logger.error("\n.env 파일에 PRODUCTHUNT_API_KEY를 추가하거나")
        logger.error("환경변수로 설정해주세요:")
        logger.error("  export PRODUCTHUNT_API_KEY='your_api_key_here'")
        return []
    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        return []


if __name__ == "__main__":
    test_scraper()
