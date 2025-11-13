"""
AI 트렌드 분석 모듈
Ollama를 사용하여 트렌드를 분석하고 솔루션 아이디어 생성
"""
import requests
import json
from typing import Dict, List, Optional
import logging
import sys
from pathlib import Path

# 설정 파일 임포트
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OLLAMA_CONFIG, CRAWLING_CONFIG

# 로거 설정
logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """트렌드 AI 분석 클래스"""

    def __init__(self, ollama_host: str = None, model: str = None):
        """
        Args:
            ollama_host: Ollama 서버 주소 (None이면 config 사용)
            model: 사용할 AI 모델명 (None이면 config 사용)
        """
        self.ollama_host = ollama_host or OLLAMA_CONFIG['host']
        self.model = model or OLLAMA_CONFIG['model']
        self.chat_url = f"{self.ollama_host}/api/chat"
        self.timeout = CRAWLING_CONFIG['request_timeout'] * 2  # AI 응답은 더 오래 걸림

    def analyze_trend(self, trend: Dict) -> Optional[Dict]:
        """
        트렌드 분석 수행

        Args:
            trend: 트렌드 데이터 딕셔너리

        Returns:
            분석 결과 딕셔너리 또는 None
        """
        try:
            prompt = self._create_analysis_prompt(trend)

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            logger.info(f"AI 분석 중: {trend.get('title', 'Unknown')}")
            response = requests.post(self.chat_url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']

                # JSON 파싱
                analysis = self._parse_json_response(ai_response)
                if analysis:
                    logger.info(f"분석 완료: {trend.get('title')}")
                    return analysis
                else:
                    logger.warning(f"JSON 파싱 실패: {trend.get('title')}")
                    return None
            else:
                logger.error(f"AI 요청 실패 ({response.status_code}): {trend.get('title')}")
                return None

        except Exception as e:
            logger.error(f"분석 오류 ({trend.get('title')}): {str(e)}")
            return None

    def generate_solutions(self, trend: Dict, analysis: Dict) -> List[Dict]:
        """
        문제 해결 솔루션 아이디어 생성

        Args:
            trend: 원본 트렌드 데이터
            analysis: 분석 결과

        Returns:
            솔루션 리스트
        """
        try:
            problems = analysis.get('problems', [])
            if not problems:
                logger.debug(f"문제점 없음, 솔루션 생성 스킵: {trend.get('title')}")
                return []

            prompt = self._create_solution_prompt(trend, analysis)

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            logger.info(f"솔루션 생성 중: {trend.get('title')}")
            response = requests.post(self.chat_url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']

                # JSON 파싱
                solutions = self._parse_json_response(ai_response)
                if solutions and 'solutions' in solutions:
                    solution_list = solutions['solutions']
                    logger.info(f"{len(solution_list)}개 솔루션 생성: {trend.get('title')}")
                    return solution_list
                else:
                    logger.warning(f"솔루션 파싱 실패: {trend.get('title')}")
                    return []
            else:
                logger.error(f"솔루션 생성 실패 ({response.status_code}): {trend.get('title')}")
                return []

        except Exception as e:
            logger.error(f"솔루션 생성 오류 ({trend.get('title')}): {str(e)}")
            return []

    def _create_analysis_prompt(self, trend: Dict) -> str:
        """트렌드 분석용 프롬프트 생성"""
        return f"""**IMPORTANT: You MUST respond in Korean language only. 반드시 한국어로만 응답하세요.**

다음 트렌드를 분석하고 JSON 형식으로만 답변해주세요:

제목: {trend.get('title', 'N/A')}
설명: {trend.get('description', 'N/A')}
카테고리: {trend.get('category', 'N/A')}
URL: {trend.get('url', 'N/A')}
메타데이터: {json.dumps(trend.get('metadata', {}), ensure_ascii=False)}

다음 형식의 JSON만 응답하세요 (다른 설명 없이, 모든 텍스트는 한국어로):
{{
  "summary": "트렌드의 핵심 내용을 1-2문장으로 요약 (한국어)",
  "category": "기술/비즈니스/사회/문화/경제 중 하나",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": ["이 트렌드가 해결하려는 문제점1", "문제점2"],
  "importance_score": 1-10 사이의 숫자 (1=매우 낮음, 5=보통, 10=매우 중요),
  "sentiment": "positive/neutral/negative"
}}

**중요도 평가 기준 (importance_score):**
- 10: 혁신적이고 산업 전반에 큰 영향을 줄 것으로 예상
- 7-9: 주목할 만한 가치가 있고 특정 분야에 중요한 영향
- 4-6: 관심을 가질 만하나 영향력이 제한적
- 1-3: 일시적이거나 영향력이 미미함

**다시 강조: 모든 응답은 반드시 한국어로 작성해야 합니다. 중국어나 다른 언어는 사용하지 마세요.**
위 형식의 JSON만 응답하세요."""

    def _create_solution_prompt(self, trend: Dict, analysis: Dict) -> str:
        """솔루션 생성용 프롬프트 생성"""
        problems_text = "\n".join([f"- {p}" for p in analysis.get('problems', [])])

        return f"""**IMPORTANT: You MUST respond in Korean language only. 반드시 한국어로만 응답하세요.**

다음 트렌드와 분석된 문제점을 기반으로 실현 가능한 솔루션 아이디어 2-3개를 JSON 형식으로 제안해주세요:

트렌드: {trend.get('title')}
요약: {analysis.get('summary')}

문제점들:
{problems_text}

다음 형식의 JSON만 응답하세요 (다른 설명 없이, 모든 텍스트는 한국어로):
{{
  "solutions": [
    {{
      "title": "솔루션 제목 (한국어)",
      "description": "솔루션에 대한 구체적인 설명 (2-3문장, 한국어)",
      "feasibility": "high/medium/low",
      "estimated_effort": "1주/1개월/3개월/6개월",
      "target_audience": "타겟 사용자층 (한국어)",
      "tech_stack": ["기술1", "기술2", "기술3"]
    }}
  ]
}}

**다시 강조: 모든 응답은 반드시 한국어로 작성해야 합니다. 중국어나 다른 언어는 사용하지 마세요.**
위 형식의 JSON만 응답하세요."""

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """AI 응답에서 JSON 추출 및 파싱"""
        try:
            # JSON 부분만 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end <= json_start:
                logger.warning("JSON 형식을 찾을 수 없음")
                return None

            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            return parsed

        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"응답 처리 오류: {str(e)}")
            return None


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    analyzer = TrendAnalyzer(ollama_host='http://localhost:11434')

    # 테스트 트렌드 데이터
    test_trend = {
        'title': 'AI 코드 자동완성 도구',
        'description': 'GitHub에서 AI가 코드를 자동으로 완성해주는 도구의 새 버전 출시',
        'category': 'AI/ML',
        'url': 'https://github.com/test/ai-autocomplete',
        'metadata': {
            'stars': 15000,
            'language': 'Python'
        }
    }

    logger.info("=" * 60)
    logger.info("트렌드 분석 테스트")
    logger.info("=" * 60)

    # 분석 수행
    analysis = analyzer.analyze_trend(test_trend)

    if analysis:
        logger.info(f"\n분석 결과:")
        logger.info(f"  - 요약: {analysis.get('summary')}")
        logger.info(f"  - 카테고리: {analysis.get('category')}")
        logger.info(f"  - 키워드: {', '.join(analysis.get('keywords', []))}")
        logger.info(f"  - 문제점: {', '.join(analysis.get('problems', []))}")
        logger.info(f"  - 중요도: {analysis.get('importance_score')}/10")
        logger.info(f"  - 감정: {analysis.get('sentiment')}")

        # 솔루션 생성
        logger.info(f"\n" + "=" * 60)
        logger.info("솔루션 생성 테스트")
        logger.info("=" * 60)

        solutions = analyzer.generate_solutions(test_trend, analysis)

        if solutions:
            logger.info(f"\n생성된 솔루션:")
            for idx, sol in enumerate(solutions, 1):
                logger.info(f"\n[솔루션 {idx}]")
                logger.info(f"  제목: {sol.get('title')}")
                logger.info(f"  설명: {sol.get('description')}")
                logger.info(f"  실현가능성: {sol.get('feasibility')}")
                logger.info(f"  예상기간: {sol.get('estimated_effort')}")
                logger.info(f"  타겟: {sol.get('target_audience')}")
                logger.info(f"  기술스택: {', '.join(sol.get('tech_stack', []))}")
    else:
        logger.error("분석 실패")
