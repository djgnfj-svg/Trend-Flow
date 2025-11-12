"""
GitHub Trending 크롤러
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


def scrape_github_trending(language: str = "", limit: int = None) -> List[Dict]:
    """
    GitHub Trending 페이지에서 트렌딩 레포지토리 크롤링

    Args:
        language: 프로그래밍 언어 필터 (예: 'python', 'javascript', '')
        limit: 가져올 최대 개수 (None이면 config의 기본값 사용)

    Returns:
        List of trending repositories
    """
    if limit is None:
        limit = CRAWLING_CONFIG['github_trending_limit']

    url = f"https://github.com/trending/{language}?since=daily"

    headers = {
        'User-Agent': CRAWLING_CONFIG['user_agent']
    }

    try:
        logger.info(f"GitHub Trending 크롤링 시작: {url}")
        response = requests.get(
            url,
            headers=headers,
            timeout=CRAWLING_CONFIG['request_timeout']
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 트렌딩 레포지토리 목록 찾기
        articles = soup.find_all('article', class_='Box-row')

        trends = []
        for idx, article in enumerate(articles[:limit]):
            try:
                # 레포지토리 이름
                h2 = article.find('h2', class_='h3')
                if not h2:
                    continue

                repo_link = h2.find('a')
                if not repo_link:
                    continue

                repo_name = repo_link.get('href', '').strip('/')
                repo_url = f"https://github.com{repo_link.get('href', '')}"

                # 설명
                description_elem = article.find('p', class_='col-9')
                description = description_elem.text.strip() if description_elem else ""

                # 언어
                language_elem = article.find('span', attrs={'itemprop': 'programmingLanguage'})
                language = language_elem.text.strip() if language_elem else "Unknown"

                # 별(stars) 수
                stars_elem = article.find('svg', class_='octicon-star')
                stars = 0
                if stars_elem:
                    stars_parent = stars_elem.find_parent('a')
                    if stars_parent:
                        stars_text = stars_parent.text.strip().replace(',', '')
                        try:
                            stars = int(stars_text.split()[0]) if stars_text else 0
                        except (ValueError, IndexError):
                            stars = 0

                # 오늘 추가된 별 수
                stars_today_elem = article.find('span', class_='d-inline-block')
                stars_today = 0
                if stars_today_elem:
                    stars_today_text = stars_today_elem.text.strip()
                    if 'stars today' in stars_today_text or 'stars' in stars_today_text:
                        try:
                            stars_today = int(stars_today_text.replace(',', '').split()[0])
                        except (ValueError, IndexError):
                            stars_today = 0

                # 포크 수
                forks = 0
                forks_elem = article.find('svg', class_='octicon-repo-forked')
                if forks_elem:
                    forks_parent = forks_elem.find_parent('a')
                    if forks_parent:
                        forks_text = forks_parent.text.strip().replace(',', '')
                        try:
                            forks = int(forks_text.split()[0]) if forks_text else 0
                        except (ValueError, IndexError):
                            forks = 0

                trend = {
                    'title': repo_name,
                    'description': description,
                    'url': repo_url,
                    'category': language,
                    'rank': idx + 1,
                    'metadata': {
                        'stars': stars,
                        'stars_today': stars_today,
                        'forks': forks,
                        'language': language
                    }
                }

                trends.append(trend)
                logger.debug(f"[{idx + 1}] {repo_name} - Stars: {stars} (+{stars_today} today)")

            except Exception as e:
                logger.warning(f"항목 파싱 오류: {str(e)}")
                continue

        logger.info(f"총 {len(trends)}개의 트렌딩 레포지토리 수집 완료")
        return trends

    except requests.RequestException as e:
        logger.error(f"크롤링 실패: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        raise


def test_scraper():
    """크롤러 테스트"""
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("=" * 60)
    logger.info("GitHub Trending 크롤러 테스트")
    logger.info("=" * 60)

    trends = scrape_github_trending(limit=5)

    logger.info(f"\n수집 결과:")
    for trend in trends:
        logger.info(f"\n제목: {trend['title']}")
        logger.info(f"설명: {trend['description'][:100]}...")
        logger.info(f"언어: {trend['category']}")
        logger.info(f"별: {trend['metadata']['stars']} (+{trend['metadata']['stars_today']} today)")

    return trends


if __name__ == "__main__":
    test_scraper()
