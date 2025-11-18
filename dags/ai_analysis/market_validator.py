"""
Market Validation Module

Google Trends를 활용한 시장 수요 분석 및 경쟁사 분석을 통해
SaaS 아이디어의 시장 타당성을 자동으로 검증합니다.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from pytrends.request import TrendReq
from googlesearch import search as google_search
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MarketValidator:
    """시장 검증을 위한 클래스"""

    def __init__(self):
        """Initialize Market Validator"""
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_search_volume_trend(self, keywords: List[str], timeframe: str = 'today 12-m') -> Dict:
        """
        Google Trends를 통해 검색량 트렌드를 분석합니다.

        Args:
            keywords: 검색할 키워드 리스트 (최대 5개)
            timeframe: 분석 기간 (예: 'today 12-m', 'today 3-m', 'today 5-y')

        Returns:
            {
                'average_interest': float,  # 평균 관심도 (0-100)
                'trend_direction': str,     # 'rising', 'stable', 'declining'
                'peak_interest': int,       # 최고 관심도
                'related_queries': list     # 연관 검색어
            }
        """
        try:
            # 최대 5개 키워드만 허용
            keywords = keywords[:5]

            logger.info(f"Analyzing search trends for: {keywords}")

            # Google Trends 데이터 가져오기
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='', gprop='')

            # 시간별 관심도 데이터
            interest_over_time_df = self.pytrends.interest_over_time()

            if interest_over_time_df.empty:
                logger.warning(f"No trend data found for keywords: {keywords}")
                return {
                    'average_interest': 0,
                    'trend_direction': 'unknown',
                    'peak_interest': 0,
                    'related_queries': []
                }

            # 평균 관심도 계산 (모든 키워드의 평균)
            interest_columns = [col for col in interest_over_time_df.columns if col != 'isPartial']
            avg_interest = interest_over_time_df[interest_columns].mean().mean()
            peak_interest = interest_over_time_df[interest_columns].max().max()

            # 트렌드 방향 분석 (최근 3개월 vs 이전 3개월)
            half_point = len(interest_over_time_df) // 2
            recent_avg = interest_over_time_df[interest_columns].iloc[half_point:].mean().mean()
            past_avg = interest_over_time_df[interest_columns].iloc[:half_point].mean().mean()

            if recent_avg > past_avg * 1.2:
                trend_direction = 'rising'
            elif recent_avg < past_avg * 0.8:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'

            # 연관 검색어 가져오기
            related_queries = []
            try:
                related_queries_df = self.pytrends.related_queries()
                for keyword in keywords:
                    if keyword in related_queries_df and related_queries_df[keyword]['top'] is not None:
                        top_queries = related_queries_df[keyword]['top']['query'].head(5).tolist()
                        related_queries.extend(top_queries)
            except Exception as e:
                logger.warning(f"Failed to get related queries: {e}")

            result = {
                'average_interest': round(float(avg_interest), 2),
                'trend_direction': trend_direction,
                'peak_interest': int(peak_interest),
                'related_queries': list(set(related_queries))[:10]  # 중복 제거 및 최대 10개
            }

            logger.info(f"Trend analysis result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing trends: {e}", exc_info=True)
            return {
                'average_interest': 0,
                'trend_direction': 'unknown',
                'peak_interest': 0,
                'related_queries': []
            }

    def find_competitors(self, idea_title: str, problem_keywords: List[str], max_results: int = 10) -> List[Dict]:
        """
        Google 검색을 통해 경쟁사를 찾습니다.

        Args:
            idea_title: 아이디어 제목
            problem_keywords: 문제 관련 키워드
            max_results: 최대 검색 결과 수

        Returns:
            [{'url': str, 'title': str, 'snippet': str}, ...]
        """
        try:
            # 검색 쿼리 생성
            query_parts = [idea_title] + problem_keywords[:3]
            search_query = ' '.join(query_parts) + ' solution software'

            logger.info(f"Searching competitors with query: {search_query}")

            competitors = []

            # Google 검색 수행
            for url in google_search(search_query, num_results=max_results, lang='en'):
                try:
                    # 간단한 메타데이터 추출
                    competitors.append({
                        'url': url,
                        'domain': self._extract_domain(url)
                    })
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Failed to process URL {url}: {e}")
                    continue

            logger.info(f"Found {len(competitors)} potential competitors")
            return competitors

        except Exception as e:
            logger.error(f"Error finding competitors: {e}", exc_info=True)
            return []

    def calculate_market_saturation(
        self,
        search_volume_score: float,
        competitor_count: int,
        trend_direction: str
    ) -> Tuple[float, str]:
        """
        시장 포화도를 계산합니다.

        Args:
            search_volume_score: 검색량 점수 (0-100)
            competitor_count: 경쟁사 수
            trend_direction: 트렌드 방향 ('rising', 'stable', 'declining')

        Returns:
            (saturation_score, market_status)
            - saturation_score: 0-100 (낮을수록 좋음, 포화도 낮음)
            - market_status: 'blue_ocean', 'growing', 'competitive', 'saturated'
        """
        # 기본 포화도 점수: 경쟁사 수 기반
        if competitor_count <= 3:
            base_score = 10
        elif competitor_count <= 10:
            base_score = 30
        elif competitor_count <= 20:
            base_score = 60
        else:
            base_score = 80

        # 검색량 조정: 검색량이 높으면 시장이 크지만 경쟁도 있을 수 있음
        if search_volume_score < 20:
            # 검색량 너무 낮음 = 수요 없음
            search_adjustment = 20
        elif search_volume_score < 40:
            # 적당한 검색량 = 좋음
            search_adjustment = -10
        elif search_volume_score < 70:
            # 높은 검색량 = 시장 크지만 경쟁 많을 수 있음
            search_adjustment = 0
        else:
            # 매우 높은 검색량 = 이미 큰 시장
            search_adjustment = 10

        # 트렌드 방향 조정
        trend_adjustment = {
            'rising': -15,      # 성장 중 = 좋음
            'stable': 0,        # 안정적
            'declining': 20,    # 하락 중 = 나쁨
            'unknown': 10       # 불명확 = 리스크
        }.get(trend_direction, 10)

        # 최종 포화도 점수 계산
        saturation_score = max(0, min(100, base_score + search_adjustment + trend_adjustment))

        # 시장 상태 결정
        if saturation_score <= 25:
            market_status = 'blue_ocean'  # 블루오션
        elif saturation_score <= 50:
            market_status = 'growing'     # 성장 시장
        elif saturation_score <= 75:
            market_status = 'competitive' # 경쟁 시장
        else:
            market_status = 'saturated'   # 포화 시장

        logger.info(f"Market saturation: {saturation_score:.1f} ({market_status})")

        return round(saturation_score, 1), market_status

    def validate_idea(self, idea: Dict) -> Dict:
        """
        SaaS 아이디어의 시장 타당성을 종합적으로 검증합니다.

        Args:
            idea: SaaS 아이디어 정보
                {
                    'title': str,
                    'problem_statement': str,
                    'keywords': list,
                    'target_audience': str
                }

        Returns:
            {
                'search_volume_score': float,
                'trend_direction': str,
                'competitor_count': int,
                'competitors': list,
                'saturation_score': float,
                'market_status': str,
                'validation_score': float,  # 0-10
                'recommendation': str
            }
        """
        logger.info(f"Starting market validation for: {idea.get('title')}")

        # 1. 키워드 준비
        keywords = idea.get('keywords', [])
        if not keywords:
            # 키워드가 없으면 제목과 문제 진술에서 추출
            keywords = self._extract_keywords(idea.get('title', ''), idea.get('problem_statement', ''))

        # 2. Google Trends 분석
        trend_data = self.get_search_volume_trend(keywords[:5])

        # 3. 경쟁사 찾기
        competitors = self.find_competitors(
            idea.get('title', ''),
            keywords,
            max_results=15
        )

        # 4. 시장 포화도 계산
        saturation_score, market_status = self.calculate_market_saturation(
            search_volume_score=trend_data['average_interest'],
            competitor_count=len(competitors),
            trend_direction=trend_data['trend_direction']
        )

        # 5. 종합 검증 점수 계산 (0-10)
        validation_score = self._calculate_validation_score(
            search_volume=trend_data['average_interest'],
            trend_direction=trend_data['trend_direction'],
            saturation_score=saturation_score,
            market_status=market_status
        )

        # 6. 추천 사항 생성
        recommendation = self._generate_recommendation(
            validation_score=validation_score,
            market_status=market_status,
            trend_direction=trend_data['trend_direction'],
            search_volume=trend_data['average_interest']
        )

        result = {
            'search_volume_score': trend_data['average_interest'],
            'trend_direction': trend_data['trend_direction'],
            'peak_interest': trend_data['peak_interest'],
            'related_queries': trend_data['related_queries'],
            'competitor_count': len(competitors),
            'competitors': [c['domain'] for c in competitors[:10]],  # 최대 10개만 저장
            'saturation_score': saturation_score,
            'market_status': market_status,
            'validation_score': validation_score,
            'recommendation': recommendation,
            'validated_at': datetime.now().isoformat()
        }

        logger.info(f"Validation complete. Score: {validation_score}/10, Status: {market_status}")
        return result

    def _extract_keywords(self, title: str, problem_statement: str) -> List[str]:
        """제목과 문제 진술에서 키워드 추출"""
        import re

        # 간단한 키워드 추출 (stopwords 제거)
        stopwords = {'a', 'an', 'the', 'for', 'to', 'of', 'in', 'on', 'at', 'is', 'are', 'was', 'were'}

        text = f"{title} {problem_statement}".lower()
        words = re.findall(r'\b\w+\b', text)
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]

        # 중복 제거 및 빈도 기반 정렬
        from collections import Counter
        word_freq = Counter(keywords)
        top_keywords = [word for word, _ in word_freq.most_common(10)]

        return top_keywords

    def _extract_domain(self, url: str) -> str:
        """URL에서 도메인 추출"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')

    def _calculate_validation_score(
        self,
        search_volume: float,
        trend_direction: str,
        saturation_score: float,
        market_status: str
    ) -> float:
        """종합 검증 점수 계산 (0-10)"""

        # 검색량 점수 (0-3점)
        if search_volume < 10:
            volume_score = 0.5  # 너무 낮음
        elif search_volume < 30:
            volume_score = 2.5  # 적당
        elif search_volume < 70:
            volume_score = 3.0  # 좋음
        else:
            volume_score = 2.0  # 너무 높음 (경쟁 많을 수 있음)

        # 트렌드 점수 (0-3점)
        trend_score = {
            'rising': 3.0,
            'stable': 2.0,
            'declining': 0.5,
            'unknown': 1.0
        }.get(trend_direction, 1.0)

        # 시장 상태 점수 (0-4점)
        status_score = {
            'blue_ocean': 4.0,
            'growing': 3.5,
            'competitive': 2.0,
            'saturated': 0.5
        }.get(market_status, 1.0)

        total_score = volume_score + trend_score + status_score
        return round(min(10, max(0, total_score)), 1)

    def _generate_recommendation(
        self,
        validation_score: float,
        market_status: str,
        trend_direction: str,
        search_volume: float
    ) -> str:
        """검증 결과 기반 추천 사항 생성"""

        if validation_score >= 8.0:
            return f"Excellent opportunity! {market_status.replace('_', ' ').title()} market with {trend_direction} trend. High potential for success."

        elif validation_score >= 6.0:
            return f"Good opportunity. {market_status.replace('_', ' ').title()} market. Consider differentiation strategy to stand out."

        elif validation_score >= 4.0:
            if market_status == 'competitive':
                return "Moderate opportunity. Competitive market requires strong differentiation and unique value proposition."
            else:
                return f"Moderate opportunity. {trend_direction.title()} trend. Validate demand with MVP before full development."

        else:
            reasons = []
            if search_volume < 10:
                reasons.append("low search volume")
            if market_status == 'saturated':
                reasons.append("saturated market")
            if trend_direction == 'declining':
                reasons.append("declining trend")

            reason_str = ", ".join(reasons) if reasons else "limited market potential"
            return f"Risky opportunity due to {reason_str}. Consider pivoting or finding a niche angle."
