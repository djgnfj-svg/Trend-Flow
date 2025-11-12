"""
AI 트렌드 분석 모듈
Ollama를 사용하여 트렌드를 분석하고 솔루션 아이디어 생성
"""
import requests
import json
from typing import Dict, List, Optional


class TrendAnalyzer:
    """트렌드 AI 분석 클래스"""

    def __init__(self, ollama_host='http://ollama:11434', model='qwen2.5:7b'):
        """
        Args:
            ollama_host: Ollama 서버 주소
            model: 사용할 AI 모델명
        """
        self.ollama_host = ollama_host
        self.model = model
        self.chat_url = f"{ollama_host}/api/chat"

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

            print(f"🤖 AI 분석 중: {trend.get('title', 'Unknown')}")
            response = requests.post(self.chat_url, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']

                # JSON 파싱
                analysis = self._parse_json_response(ai_response)
                if analysis:
                    print(f"✅ 분석 완료: {trend.get('title')}")
                    return analysis
                else:
                    print(f"⚠️  JSON 파싱 실패: {trend.get('title')}")
                    return None
            else:
                print(f"❌ AI 요청 실패 ({response.status_code}): {trend.get('title')}")
                return None

        except Exception as e:
            print(f"❌ 분석 오류 ({trend.get('title')}): {str(e)}")
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
                print(f"⏭️  문제점 없음, 솔루션 생성 스킵: {trend.get('title')}")
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

            print(f"💡 솔루션 생성 중: {trend.get('title')}")
            response = requests.post(self.chat_url, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']

                # JSON 파싱
                solutions = self._parse_json_response(ai_response)
                if solutions and 'solutions' in solutions:
                    solution_list = solutions['solutions']
                    print(f"✅ {len(solution_list)}개 솔루션 생성: {trend.get('title')}")
                    return solution_list
                else:
                    print(f"⚠️  솔루션 파싱 실패: {trend.get('title')}")
                    return []
            else:
                print(f"❌ 솔루션 생성 실패 ({response.status_code}): {trend.get('title')}")
                return []

        except Exception as e:
            print(f"❌ 솔루션 생성 오류 ({trend.get('title')}): {str(e)}")
            return []

    def _create_analysis_prompt(self, trend: Dict) -> str:
        """트렌드 분석용 프롬프트 생성"""
        return f"""다음 트렌드를 분석하고 JSON 형식으로만 답변해주세요:

제목: {trend.get('title', 'N/A')}
설명: {trend.get('description', 'N/A')}
카테고리: {trend.get('category', 'N/A')}
URL: {trend.get('url', 'N/A')}
메타데이터: {json.dumps(trend.get('metadata', {}), ensure_ascii=False)}

다음 형식의 JSON만 응답하세요 (다른 설명 없이):
{{
  "summary": "트렌드의 핵심 내용을 1-2문장으로 요약",
  "category": "기술/비즈니스/사회/문화/경제 중 하나",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": ["이 트렌드가 해결하려는 문제점1", "문제점2"],
  "importance_score": 8,
  "sentiment": "positive/neutral/negative"
}}

위 형식의 JSON만 응답하세요."""

    def _create_solution_prompt(self, trend: Dict, analysis: Dict) -> str:
        """솔루션 생성용 프롬프트 생성"""
        problems_text = "\n".join([f"- {p}" for p in analysis.get('problems', [])])

        return f"""다음 트렌드와 분석된 문제점을 기반으로 실현 가능한 솔루션 아이디어 2-3개를 JSON 형식으로 제안해주세요:

트렌드: {trend.get('title')}
요약: {analysis.get('summary')}

문제점들:
{problems_text}

다음 형식의 JSON만 응답하세요 (다른 설명 없이):
{{
  "solutions": [
    {{
      "title": "솔루션 제목",
      "description": "솔루션에 대한 구체적인 설명 (2-3문장)",
      "feasibility": "high/medium/low",
      "estimated_effort": "1주/1개월/3개월/6개월",
      "target_audience": "타겟 사용자층",
      "tech_stack": ["기술1", "기술2", "기술3"]
    }}
  ]
}}

위 형식의 JSON만 응답하세요."""

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """AI 응답에서 JSON 추출 및 파싱"""
        try:
            # JSON 부분만 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end <= json_start:
                print(f"⚠️  JSON 형식을 찾을 수 없음")
                return None

            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            return parsed

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            print(f"⚠️  응답 처리 오류: {str(e)}")
            return None


if __name__ == "__main__":
    # 테스트
    analyzer = TrendAnalyzer(ollama_host='http://localhost:11434', model='qwen2.5:7b')

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

    print("=" * 60)
    print("트렌드 분석 테스트")
    print("=" * 60)

    # 분석 수행
    analysis = analyzer.analyze_trend(test_trend)

    if analysis:
        print(f"\n📊 분석 결과:")
        print(f"  - 요약: {analysis.get('summary')}")
        print(f"  - 카테고리: {analysis.get('category')}")
        print(f"  - 키워드: {', '.join(analysis.get('keywords', []))}")
        print(f"  - 문제점: {', '.join(analysis.get('problems', []))}")
        print(f"  - 중요도: {analysis.get('importance_score')}/10")
        print(f"  - 감정: {analysis.get('sentiment')}")

        # 솔루션 생성
        print(f"\n" + "=" * 60)
        print("솔루션 생성 테스트")
        print("=" * 60)

        solutions = analyzer.generate_solutions(test_trend, analysis)

        if solutions:
            print(f"\n💡 생성된 솔루션:")
            for idx, sol in enumerate(solutions, 1):
                print(f"\n[솔루션 {idx}]")
                print(f"  제목: {sol.get('title')}")
                print(f"  설명: {sol.get('description')}")
                print(f"  실현가능성: {sol.get('feasibility')}")
                print(f"  예상기간: {sol.get('estimated_effort')}")
                print(f"  타겟: {sol.get('target_audience')}")
                print(f"  기술스택: {', '.join(sol.get('tech_stack', []))}")
    else:
        print("❌ 분석 실패")
