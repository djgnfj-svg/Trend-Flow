"""
Reddit Trending - Reddit JSON API 사용
인기 서브레딧에서 핫 포스트 수집
"""
import requests
from typing import List, Dict
import logging
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


def scrape_reddit_trending(subreddits: List[str] = None, limit_per_subreddit: int = None) -> List[Dict]:
    """
    Reddit JSON API를 사용하여 인기 포스트 수집

    Args:
        subreddits: 수집할 서브레딧 리스트 (None이면 기본값 사용)
        limit_per_subreddit: 각 서브레딧당 수집할 개수 (None이면 config 사용)

    Returns:
        List of trending posts
    """
    if subreddits is None:
        subreddits = CRAWLING_CONFIG.get('reddit_subreddits', ['technology', 'programming', 'SideProject'])

    if limit_per_subreddit is None:
        limit_per_subreddit = CRAWLING_CONFIG.get('reddit_limit_per_subreddit', 10)

    logger.info(f"Reddit 수집 시작 - 서브레딧: {subreddits}, 개수: {limit_per_subreddit}개/서브레딧")

    all_trends = []

    for subreddit in subreddits:
        try:
            trends = fetch_from_subreddit(subreddit, limit_per_subreddit)
            all_trends.extend(trends)
            logger.info(f"r/{subreddit}에서 {len(trends)}개 포스트 수집 완료")
        except Exception as e:
            logger.error(f"r/{subreddit} 수집 실패: {str(e)}")
            continue

    logger.info(f"총 {len(all_trends)}개 Reddit 포스트 수집 완료")
    return all_trends


def fetch_from_subreddit(subreddit: str, limit: int) -> List[Dict]:
    """
    특정 서브레딧에서 핫 포스트 가져오기

    Args:
        subreddit: 서브레딧 이름
        limit: 가져올 개수

    Returns:
        List of posts

    Raises:
        requests.RequestException: API 요청 실패 시
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"

    headers = {
        'User-Agent': CRAWLING_CONFIG['user_agent'],
    }

    params = {
        'limit': limit
    }

    try:
        logger.debug(f"Reddit API 호출 중... (r/{subreddit})")
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=CRAWLING_CONFIG['request_timeout']
        )
        response.raise_for_status()

        data = response.json()
        posts = data.get('data', {}).get('children', [])

        trends = []
        for idx, post_wrapper in enumerate(posts[:limit]):
            post = post_wrapper.get('data', {})

            # 광고 또는 스티키 포스트 제외
            if post.get('is_video') or post.get('stickied') or post.get('promoted'):
                continue

            # 자체 포스트(self post)인지 링크 포스트인지 확인
            is_self = post.get('is_self', False)
            post_url = post.get('url', '')

            # 자체 포스트면 Reddit permalink 사용
            if is_self:
                post_url = f"https://www.reddit.com{post.get('permalink', '')}"

            trend = {
                'title': post.get('title', ''),
                'description': post.get('selftext', '')[:500] if is_self else '',  # 최대 500자
                'url': post_url,
                'category': f"r/{subreddit}",
                'rank': idx + 1,
                'metadata': {
                    'score': post.get('score', 0),  # 업보트 점수
                    'num_comments': post.get('num_comments', 0),
                    'author': post.get('author', '[deleted]'),
                    'created_utc': post.get('created_utc', 0),
                    'subreddit': subreddit,
                    'is_self': is_self,
                    'upvote_ratio': post.get('upvote_ratio', 0.0),
                    'awards': len(post.get('all_awardings', [])),
                }
            }
            trends.append(trend)
            logger.debug(f"[{idx + 1}] {trend['title'][:50]}... - Score: {trend['metadata']['score']}")

        return trends

    except requests.RequestException as e:
        error_msg = f"Reddit API 요청 실패 (r/{subreddit}): {str(e)}"
        logger.error(error_msg)

        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"응답 코드: {e.response.status_code}")
            try:
                error_data = e.response.json()
                logger.error(f"에러 응답: {error_data}")
            except:
                pass

        raise
    except Exception as e:
        error_msg = f"Reddit 데이터 처리 중 오류 (r/{subreddit}): {str(e)}"
        logger.error(error_msg)
        raise


def test_scraper():
    """크롤러 테스트"""
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("=" * 60)
    logger.info("Reddit Trending 테스트")
    logger.info("=" * 60)

    try:
        trends = scrape_reddit_trending(subreddits=['technology', 'programming'], limit_per_subreddit=5)

        logger.info(f"\n수집 결과: {len(trends)}개")
        for trend in trends:
            logger.info(f"\n#{trend['rank']} [{trend['category']}] {trend['title']}")
            if trend['description']:
                logger.info(f"설명: {trend['description'][:100]}...")
            logger.info(f"URL: {trend['url']}")
            logger.info(f"점수: {trend['metadata']['score']}, 댓글: {trend['metadata']['num_comments']}")

        return trends
    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        return []


if __name__ == "__main__":
    test_scraper()
