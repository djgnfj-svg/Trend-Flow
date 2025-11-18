"""
Reddit Pain Point Collector
실제 사용자의 불만과 문제점을 수집
"""
import praw
import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)

# Reddit API Credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'PainPointFinder/1.0')

# 타겟 Subreddit (우선순위순)
TARGET_SUBREDDITS = [
    'SideProject',      # 사이드 프로젝트 아이디어
    'Entrepreneur',     # 창업자들의 고민
    'startups',         # 스타트업 문제
    'SaaS',             # SaaS 피드백
    'smallbusiness',    # 소상공인 문제
    'freelance',        # 프리랜서 문제
    'webdev',           # 개발자 도구
    'productivity',     # 생산성 도구
]

# Pain Point 키워드
PAIN_KEYWORDS = [
    'pain', 'problem', 'frustrated', 'frustrating', 'annoying',
    'wish there was', 'need', 'struggle', 'struggling', 'difficult',
    'hate', 'tired of', 'wasting time', 'looking for', 'help with',
    'better way', 'is there', 'how do you', 'advice', 'recommendation'
]


def create_reddit_client():
    """Reddit API 클라이언트 생성"""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        error_msg = (
            "Reddit API credentials가 설정되지 않았습니다.\n"
            "환경변수 REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET을 설정해주세요.\n"
            "발급: https://www.reddit.com/prefs/apps"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    logger.info(f"Reddit API 클라이언트 생성 완료 (User: {reddit.user.me()})")
    return reddit


def has_pain_keywords(text: str) -> bool:
    """텍스트에 Pain Point 키워드가 있는지 확인"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PAIN_KEYWORDS)


def collect_reddit_posts(subreddit_name: str, limit: int = None) -> List[Dict]:
    """
    특정 Subreddit에서 Pain Point 포스트 수집

    Args:
        subreddit_name: Subreddit 이름
        limit: 수집할 최대 개수

    Returns:
        List of posts with pain points
    """
    if limit is None:
        limit = CRAWLING_CONFIG.get('reddit_limit_per_subreddit', 10)

    try:
        reddit = create_reddit_client()
        subreddit = reddit.subreddit(subreddit_name)

        logger.info(f"r/{subreddit_name} 에서 포스트 수집 중...")

        posts = []
        collected = 0

        # 최근 일주일 내 Hot 포스트 확인
        for submission in subreddit.hot(limit=100):
            # 최근 7일 내 게시글만
            post_time = datetime.fromtimestamp(submission.created_utc)
            if datetime.now() - post_time > timedelta(days=7):
                continue

            # Upvote 10개 이상만
            if submission.score < 10:
                continue

            # 제목이나 본문에 Pain Point 키워드가 있는지 확인
            title_text = submission.title
            body_text = submission.selftext or ""
            full_text = f"{title_text} {body_text}"

            if not has_pain_keywords(full_text):
                continue

            # 데이터 수집
            post_data = {
                'content_type': 'post',
                'title': title_text,
                'body': body_text,
                'author': str(submission.author) if submission.author else '[deleted]',
                'url': f"https://www.reddit.com{submission.permalink}",
                'external_id': submission.id,
                'metadata': {
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'subreddit': subreddit_name,
                    'upvote_ratio': submission.upvote_ratio,
                }
            }

            # 상위 댓글도 수집 (추가 컨텍스트)
            top_comments = []
            submission.comments.replace_more(limit=0)  # "more comments" 링크 제거
            for comment in submission.comments[:3]:  # 상위 3개 댓글
                if isinstance(comment, praw.models.Comment):
                    top_comments.append({
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                    })

            post_data['metadata']['top_comments'] = top_comments

            posts.append(post_data)
            collected += 1

            logger.debug(f"[{collected}] {title_text[:50]}... (Score: {submission.score})")

            if collected >= limit:
                break

        logger.info(f"r/{subreddit_name} 수집 완료: {len(posts)}개")
        return posts

    except Exception as e:
        logger.error(f"r/{subreddit_name} 수집 실패: {str(e)}")
        return []


def collect_all_subreddits(subreddits: List[str] = None) -> List[Dict]:
    """
    여러 Subreddit에서 Pain Point 수집

    Args:
        subreddits: Subreddit 목록 (None이면 기본 목록 사용)

    Returns:
        List of all collected posts
    """
    if subreddits is None:
        subreddits = TARGET_SUBREDDITS

    all_posts = []

    logger.info("=" * 60)
    logger.info(f"Reddit Pain Point 수집 시작 ({len(subreddits)}개 Subreddit)")
    logger.info("=" * 60)

    for subreddit in subreddits:
        posts = collect_reddit_posts(subreddit)
        all_posts.extend(posts)

    logger.info("=" * 60)
    logger.info(f"전체 수집 완료: {len(all_posts)}개 포스트")
    logger.info("=" * 60)

    return all_posts


def test_collector():
    """콜렉터 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("=" * 60)
    logger.info("Reddit Pain Point Collector 테스트")
    logger.info("=" * 60)

    try:
        # 1개 Subreddit만 테스트
        posts = collect_reddit_posts('SideProject', limit=5)

        logger.info(f"\n수집 결과: {len(posts)}개")

        for i, post in enumerate(posts, 1):
            logger.info(f"\n[{i}] {post['title']}")
            logger.info(f"Author: {post['author']}")
            logger.info(f"Score: {post['metadata']['score']}, Comments: {post['metadata']['num_comments']}")
            logger.info(f"Body: {post['body'][:200]}...")
            logger.info(f"URL: {post['url']}")

            if post['metadata']['top_comments']:
                logger.info(f"Top Comment: {post['metadata']['top_comments'][0]['body'][:100]}...")

        return posts

    except ValueError as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        logger.error("\n.env 파일에 Reddit API credentials를 추가하거나")
        logger.error("환경변수로 설정해주세요:")
        logger.error("  export REDDIT_CLIENT_ID='your_client_id'")
        logger.error("  export REDDIT_CLIENT_SECRET='your_client_secret'")
        return []

    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        return []


if __name__ == "__main__":
    test_collector()
