"""
Indie Hackers Collector
인디 메이커들의 성공/실패 스토리 및 Pain Point 수집
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from typing import List, Dict
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)

# Indie Hackers 설정
BASE_URL = "https://www.indiehackers.com"
FORUM_URL = f"{BASE_URL}/forum"


def create_driver():
    """Selenium WebDriver 생성"""
    options = Options()
    options.add_argument('--headless')  # 백그라운드 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(f"user-agent={CRAWLING_CONFIG['user_agent']}")

    driver = webdriver.Chrome(options=options)
    logger.info("Selenium WebDriver 생성 완료")
    return driver


def collect_forum_posts(limit: int = None) -> List[Dict]:
    """
    Indie Hackers 포럼 포스트 수집

    Args:
        limit: 수집할 최대 개수

    Returns:
        포스트 리스트
    """
    if limit is None:
        limit = CRAWLING_CONFIG.get('indie_hackers_limit', 20)

    driver = None
    posts = []

    try:
        driver = create_driver()
        logger.info(f"Indie Hackers 포럼 접속 중... ({FORUM_URL})")

        # 포럼 페이지 로드
        driver.get(FORUM_URL)
        time.sleep(3)  # 페이지 로딩 대기

        # 포스트 목록 가져오기
        logger.info("포스트 목록 수집 중...")

        # Indie Hackers의 포스트 요소 찾기 (실제 HTML 구조에 따라 조정 필요)
        post_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='post']")

        if not post_elements:
            # 대체 선택자 시도
            post_elements = driver.find_elements(By.CSS_SELECTOR, "article")

        logger.info(f"포스트 요소 {len(post_elements)}개 발견")

        collected = 0

        for post_elem in post_elements[:limit * 2]:  # 여유있게 가져오기
            try:
                # 제목 추출
                title_elem = post_elem.find_element(By.CSS_SELECTOR, "h2, h3, a[class*='title']")
                title = title_elem.text.strip()

                if not title:
                    continue

                # URL 추출
                try:
                    link = title_elem.get_attribute('href')
                    if not link:
                        link = post_elem.find_element(By.TAG_NAME, 'a').get_attribute('href')

                    # 상대 경로를 절대 경로로 변환
                    if link and not link.startswith('http'):
                        link = BASE_URL + link
                except:
                    link = ""

                # 작성자 추출
                try:
                    author_elem = post_elem.find_element(By.CSS_SELECTOR, "[class*='author'], [class*='user']")
                    author = author_elem.text.strip()
                except:
                    author = "Unknown"

                # 본문 미리보기 추출
                try:
                    body_elem = post_elem.find_element(By.CSS_SELECTOR, "p, div[class*='content'], div[class*='body']")
                    body = body_elem.text.strip()
                except:
                    body = ""

                # 메타데이터 추출 (댓글 수, 좋아요 등)
                metadata = {}

                try:
                    comments_elem = post_elem.find_element(By.CSS_SELECTOR, "[class*='comment']")
                    comments_text = comments_elem.text
                    # 숫자 추출
                    import re
                    comments_match = re.search(r'(\d+)', comments_text)
                    if comments_match:
                        metadata['comments'] = int(comments_match.group(1))
                except:
                    metadata['comments'] = 0

                # 포스트 ID 생성 (URL에서 추출)
                post_id = link.split('/')[-1] if link else f"post_{collected}"

                post_data = {
                    'content_type': 'post',
                    'title': title,
                    'body': body,
                    'author': author,
                    'url': link,
                    'external_id': post_id,
                    'metadata': metadata
                }

                posts.append(post_data)
                collected += 1

                logger.debug(f"[{collected}] {title[:50]}...")

                if collected >= limit:
                    break

            except Exception as e:
                logger.warning(f"포스트 파싱 실패: {str(e)}")
                continue

        logger.info(f"Indie Hackers 포럼 수집 완료: {len(posts)}개")
        return posts

    except Exception as e:
        logger.error(f"Indie Hackers 수집 실패: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()


def collect_product_stories(limit: int = 10) -> List[Dict]:
    """
    Indie Hackers 제품 스토리 수집
    (인디 메이커들의 성공/실패 인터뷰)

    Args:
        limit: 수집할 최대 개수

    Returns:
        스토리 리스트
    """
    driver = None
    stories = []

    try:
        driver = create_driver()
        interviews_url = f"{BASE_URL}/interviews"

        logger.info(f"Indie Hackers 인터뷰 페이지 접속 중... ({interviews_url})")
        driver.get(interviews_url)
        time.sleep(3)

        # 인터뷰 목록 가져오기
        story_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='interview'], article")

        logger.info(f"인터뷰 요소 {len(story_elements)}개 발견")

        collected = 0

        for story_elem in story_elements[:limit * 2]:
            try:
                # 제목 추출
                title_elem = story_elem.find_element(By.CSS_SELECTOR, "h2, h3")
                title = title_elem.text.strip()

                if not title:
                    continue

                # URL 추출
                try:
                    link = story_elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if link and not link.startswith('http'):
                        link = BASE_URL + link
                except:
                    link = ""

                # 작성자/인터뷰이 추출
                try:
                    author_elem = story_elem.find_element(By.CSS_SELECTOR, "[class*='founder'], [class*='author']")
                    author = author_elem.text.strip()
                except:
                    author = "Unknown"

                # 요약 추출
                try:
                    summary_elem = story_elem.find_element(By.CSS_SELECTOR, "p, div[class*='summary']")
                    summary = summary_elem.text.strip()
                except:
                    summary = ""

                # 스토리 ID
                story_id = link.split('/')[-1] if link else f"story_{collected}"

                story_data = {
                    'content_type': 'interview',
                    'title': title,
                    'body': summary,
                    'author': author,
                    'url': link,
                    'external_id': story_id,
                    'metadata': {
                        'type': 'interview'
                    }
                }

                stories.append(story_data)
                collected += 1

                logger.debug(f"[{collected}] {title[:50]}...")

                if collected >= limit:
                    break

            except Exception as e:
                logger.warning(f"인터뷰 파싱 실패: {str(e)}")
                continue

        logger.info(f"Indie Hackers 인터뷰 수집 완료: {len(stories)}개")
        return stories

    except Exception as e:
        logger.error(f"Indie Hackers 인터뷰 수집 실패: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()


def collect_all_indie_hackers(forum_limit: int = 15, story_limit: int = 5) -> List[Dict]:
    """
    Indie Hackers에서 모든 콘텐츠 수집

    Args:
        forum_limit: 포럼 포스트 수집 개수
        story_limit: 인터뷰 수집 개수

    Returns:
        전체 콘텐츠 리스트
    """
    logger.info("=" * 60)
    logger.info("Indie Hackers 전체 수집 시작")
    logger.info("=" * 60)

    all_contents = []

    # 1. 포럼 포스트 수집
    forum_posts = collect_forum_posts(limit=forum_limit)
    all_contents.extend(forum_posts)

    # 2. 제품 스토리/인터뷰 수집
    stories = collect_product_stories(limit=story_limit)
    all_contents.extend(stories)

    logger.info("=" * 60)
    logger.info(f"Indie Hackers 전체 수집 완료: {len(all_contents)}개")
    logger.info(f"  - 포럼 포스트: {len(forum_posts)}개")
    logger.info(f"  - 인터뷰/스토리: {len(stories)}개")
    logger.info("=" * 60)

    return all_contents


def test_collector():
    """크롤러 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("=" * 60)
    logger.info("Indie Hackers Collector 테스트")
    logger.info("=" * 60)

    try:
        # 포럼 포스트 수집 테스트
        contents = collect_all_indie_hackers(forum_limit=5, story_limit=3)

        logger.info(f"\n수집 결과: {len(contents)}개")

        for i, content in enumerate(contents, 1):
            logger.info(f"\n[{i}] {content['title']}")
            logger.info(f"Type: {content['content_type']}")
            logger.info(f"Author: {content['author']}")
            logger.info(f"Body: {content['body'][:100]}...")
            logger.info(f"URL: {content['url']}")

        return contents

    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    test_collector()
