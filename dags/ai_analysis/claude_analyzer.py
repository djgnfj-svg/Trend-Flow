"""
Claude API Pain Point Analyzer
Claude API를 사용하여 Pain Point 추출 및 SaaS 아이디어 생성
"""
import anthropic
import os
import json
import logging
from typing import Dict, List, Optional

# 로거 설정
logger = logging.getLogger(__name__)

# API 키
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', '4096'))
CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))


class ClaudeAnalyzer:
    """Claude API를 사용한 Pain Point 분석기"""

    def __init__(self):
        """초기화"""
        if not ANTHROPIC_API_KEY:
            error_msg = (
                "Anthropic API Key가 설정되지 않았습니다.\n"
                "환경변수 ANTHROPIC_API_KEY를 설정해주세요.\n"
                "발급: https://console.anthropic.com/"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        logger.info(f"Claude Analyzer 초기화 완료 (Model: {self.model})")

    def extract_pain_point(
        self,
        content: Dict,
        similar_pain_points: List[Dict] = None
    ) -> Optional[Dict]:
        """
        콘텐츠에서 Pain Point 추출

        Args:
            content: 원본 콘텐츠 (title, body, metadata)
            similar_pain_points: 유사한 과거 Pain Point들 (RAG)

        Returns:
            Pain Point 데이터 또는 None
        """
        logger.info(f"Pain Point 추출 중: {content.get('title', '')[:50]}...")

        # 유사 Pain Point 컨텍스트 생성
        context = ""
        if similar_pain_points:
            context = "\n".join([
                f"- {pp.get('problem_statement', '')}"
                for pp in similar_pain_points[:5]
            ])

        # 프롬프트 작성
        prompt = self._create_pain_point_prompt(content, context)

        try:
            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=CLAUDE_TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 파싱
            response_text = response.content[0].text

            # JSON 추출 (마크다운 코드 블록 제거)
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)

            # Pain Point가 없는 경우
            if not result.get('has_pain_point', False):
                logger.info("Pain Point 없음")
                return None

            logger.info(f"Pain Point 추출 완료: {result.get('problem_statement', '')[:50]}...")
            logger.info(f"Confidence: {result.get('confidence_score', 0)}, Severity: {result.get('severity', '')}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            logger.error(f"Response: {response_text[:500]}")
            return None

        except Exception as e:
            logger.error(f"Pain Point 추출 실패: {str(e)}")
            return None

    def generate_saas_ideas(
        self,
        pain_point: Dict,
        similar_products: List[str] = None
    ) -> List[Dict]:
        """
        Pain Point를 해결하는 SaaS 아이디어 생성

        Args:
            pain_point: Pain Point 데이터
            similar_products: 유사 제품 목록

        Returns:
            List of SaaS ideas (최대 3개)
        """
        logger.info(f"SaaS 아이디어 생성 중: {pain_point.get('problem_statement', '')[:50]}...")

        # 프롬프트 작성
        prompt = self._create_idea_generation_prompt(pain_point, similar_products)

        try:
            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=CLAUDE_TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 파싱
            response_text = response.content[0].text

            # JSON 추출
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)
            ideas = result.get('ideas', [])

            logger.info(f"SaaS 아이디어 {len(ideas)}개 생성 완료")

            for i, idea in enumerate(ideas, 1):
                logger.info(f"  [{i}] {idea.get('title', '')} (Score: {idea.get('overall_score', 0)}/10)")

            return ideas

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            logger.error(f"Response: {response_text[:500]}")
            return []

        except Exception as e:
            logger.error(f"아이디어 생성 실패: {str(e)}")
            return []

    def _create_pain_point_prompt(self, content: Dict, context: str = "") -> str:
        """Pain Point 추출 프롬프트 생성"""
        prompt = f"""당신은 SaaS 아이디어 발굴 전문가입니다.

다음 콘텐츠를 분석하여 **실제 사용자의 Pain Point**를 추출하세요.

"""

        if context:
            prompt += f"""<유사한 과거 Pain Point들>
{context}
</유사한 과거 Pain Point들>

"""

        prompt += f"""<분석할 콘텐츠>
제목: {content.get('title', '')}
본문: {content.get('body', '')}
출처: {content.get('metadata', {}).get('subreddit', 'Unknown')}
</분석할 콘텐츠>

다음 형식의 JSON으로 응답하세요:

```json
{{
  "has_pain_point": true,
  "problem_statement": "한 문장으로 문제 요약",
  "problem_detail": "상세 설명",
  "affected_users": "영향받는 사용자 (예: 프리랜서, 소상공인, 개발자)",
  "frequency": "daily",
  "severity": "high",
  "market_size": "medium",
  "willingness_to_pay": "medium",
  "existing_solutions": ["기존 솔루션1", "기존 솔루션2"],
  "solution_gaps": "기존 솔루션이 해결하지 못하는 점",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "category": "productivity",
  "confidence_score": 0.85
}}
```

**판단 기준**:
1. 명확한 문제가 있는가?
2. 해결할 가치가 있는가?
3. 여러 사람이 겪는 문제인가?
4. 기술적으로 해결 가능한가?
5. 비즈니스 기회가 있는가?

**frequency**: daily, weekly, monthly, occasional 중 선택
**severity**: critical, high, medium, low 중 선택
**market_size**: large, medium, small, niche 중 선택
**willingness_to_pay**: high, medium, low, unknown 중 선택
**category**: productivity, finance, communication, marketing, development, healthcare, education, ecommerce 등
**confidence_score**: 0.00 ~ 1.00 (이 Pain Point가 실제 비즈니스 기회인지 확신하는 정도)

Pain Point가 없거나 명확하지 않으면 `has_pain_point: false`로 응답하세요.
"""

        return prompt

    def _create_idea_generation_prompt(
        self,
        pain_point: Dict,
        similar_products: List[str] = None
    ) -> str:
        """SaaS 아이디어 생성 프롬프트 생성"""
        prompt = f"""다음 Pain Point를 해결하는 **구체적인 SaaS/Micro Service 아이디어**를 3개 생성하세요.

<Pain Point>
문제: {pain_point.get('problem_statement', '')}
상세: {pain_point.get('problem_detail', '')}
영향받는 사용자: {pain_point.get('affected_users', '')}
심각도: {pain_point.get('severity', '')}
빈도: {pain_point.get('frequency', '')}
시장 크기: {pain_point.get('market_size', '')}
기존 솔루션: {', '.join(pain_point.get('existing_solutions', []))}
솔루션 갭: {pain_point.get('solution_gaps', '')}
</Pain Point>

"""

        if similar_products:
            prompt += f"""<유사 제품들>
{', '.join(similar_products)}
</유사 제품들>

"""

        prompt += """각 아이디어는 다음 형식의 JSON으로 응답하세요:

```json
{
  "ideas": [
    {
      "title": "서비스 이름",
      "tagline": "한 줄 설명 (10단어 이내)",
      "description": "상세 설명 (3-5문장)",
      "business_model": "subscription",
      "pricing_model": "구체적인 가격 전략 (예: Basic $9/월, Pro $29/월)",
      "estimated_monthly_revenue": "$1K-$10K",
      "tech_stack": ["React", "Node.js", "PostgreSQL"],
      "complexity": "moderate",
      "estimated_dev_time": "1개월",
      "mvp_features": [
        "핵심 기능 1",
        "핵심 기능 2",
        "핵심 기능 3"
      ],
      "mvp_description": "MVP 설명 (2-3문장)",
      "target_audience": "타겟 고객 상세",
      "go_to_market_strategy": "어떻게 고객을 확보할 것인가",
      "competition_level": "medium",
      "differentiation": "기존 솔루션과 차별점",
      "feasibility_score": 8,
      "market_score": 7,
      "overall_score": 8,
      "tags": ["tag1", "tag2"],
      "similar_products": ["Notion", "Airtable"]
    }
  ]
}
```

**요구사항**:
1. 각 아이디어는 서로 다른 접근 방식
2. 최소 1개는 simple complexity
3. MVP는 1-3개월 내 개발 가능한 범위
4. 실제 비즈니스 모델 포함 (가격 명시)
5. 경쟁사 대비 명확한 차별점
6. feasibility_score: 기술적 실행 가능성 (1-10)
7. market_score: 시장 기회 (1-10)
8. overall_score: 종합 점수 (1-10)

**business_model**: subscription, freemium, one-time, usage-based 중 선택
**complexity**: simple, moderate, complex 중 선택
**estimated_dev_time**: 1주, 2주, 1개월, 2개월, 3개월, 6개월+ 중 선택
**estimated_monthly_revenue**: $0-$1K, $1K-$10K, $10K-$50K, $50K+ 중 선택
**competition_level**: low, medium, high 중 선택
"""

        return prompt


def test_analyzer():
    """Analyzer 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("=" * 60)
    logger.info("Claude Analyzer 테스트")
    logger.info("=" * 60)

    try:
        analyzer = ClaudeAnalyzer()

        # 테스트 콘텐츠
        test_content = {
            'title': "I'm spending 5 hours a week on invoicing. There has to be a better way",
            'body': """I run a small consulting business and manually create invoices in Excel.
            Then I have to email them, track payments, send reminders... It's so time-consuming.
            I tried QuickBooks but it's too expensive and complicated for my needs.
            Are there any simple, affordable solutions for freelancers?""",
            'metadata': {
                'subreddit': 'freelance',
                'score': 45,
                'num_comments': 23
            }
        }

        # Pain Point 추출
        pain_point = analyzer.extract_pain_point(test_content)

        if pain_point:
            logger.info("\n" + "=" * 60)
            logger.info("Pain Point 추출 결과")
            logger.info("=" * 60)
            logger.info(f"문제: {pain_point.get('problem_statement', '')}")
            logger.info(f"사용자: {pain_point.get('affected_users', '')}")
            logger.info(f"심각도: {pain_point.get('severity', '')} / 빈도: {pain_point.get('frequency', '')}")
            logger.info(f"시장 크기: {pain_point.get('market_size', '')}")
            logger.info(f"신뢰도: {pain_point.get('confidence_score', 0)}")

            # SaaS 아이디어 생성
            ideas = analyzer.generate_saas_ideas(pain_point)

            if ideas:
                logger.info("\n" + "=" * 60)
                logger.info("SaaS 아이디어 생성 결과")
                logger.info("=" * 60)

                for i, idea in enumerate(ideas, 1):
                    logger.info(f"\n[아이디어 {i}] {idea.get('title', '')}")
                    logger.info(f"Tagline: {idea.get('tagline', '')}")
                    logger.info(f"비즈니스 모델: {idea.get('business_model', '')} - {idea.get('pricing_model', '')}")
                    logger.info(f"개발 기간: {idea.get('estimated_dev_time', '')} ({idea.get('complexity', '')})")
                    logger.info(f"점수: {idea.get('overall_score', 0)}/10 (Feasibility: {idea.get('feasibility_score', 0)}, Market: {idea.get('market_score', 0)})")
                    logger.info(f"MVP 기능: {', '.join(idea.get('mvp_features', []))}")
        else:
            logger.info("Pain Point를 찾지 못했습니다.")

    except ValueError as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        logger.error("\n.env 파일에 ANTHROPIC_API_KEY를 추가하거나")
        logger.error("환경변수로 설정해주세요:")
        logger.error("  export ANTHROPIC_API_KEY='your_api_key'")

    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_analyzer()
