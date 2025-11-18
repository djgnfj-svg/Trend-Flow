"""
Multi-Agent AI System

여러 전문화된 AI 에이전트가 협력하여 Pain Point 분석 및 아이디어 생성 품질을 향상시킵니다.

Agents:
- Problem Analyzer: Pain Point 추출 및 분석 전문
- Market Researcher: 시장 조사 및 경쟁 분석 전문
- Solution Designer: 혁신적인 솔루션 설계 전문
- Quality Reviewer: 최종 품질 검증 전문
"""

import os
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class BaseAgent:
    """모든 에이전트의 기본 클래스"""

    def __init__(self, name: str, role: str, expertise: str):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def think(self, prompt: str, temperature: float = 0.7) -> str:
        """에이전트가 주어진 프롬프트에 대해 생각합니다."""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=temperature,
                system=f"You are {self.name}, a {self.role}. Your expertise: {self.expertise}",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"{self.name} thinking error: {e}")
            return ""


class ProblemAnalyzerAgent(BaseAgent):
    """Pain Point 추출 및 분석 전문 에이전트"""

    def __init__(self):
        super().__init__(
            name="Problem Analyzer",
            role="Pain Point Extraction Specialist",
            expertise="Deep understanding of user problems, pain severity assessment, and problem statement formulation"
        )

    def analyze_content(self, content: Dict, similar_contexts: List[Dict] = None) -> Dict:
        """
        콘텐츠를 분석하여 Pain Point를 추출합니다.

        Args:
            content: 분석할 콘텐츠
            similar_contexts: RAG에서 가져온 유사한 컨텍스트

        Returns:
            Pain Point 분석 결과
        """
        logger.info(f"[{self.name}] Analyzing content: {content.get('title', '')[:50]}...")

        # 유사 컨텍스트 요약
        context_summary = ""
        if similar_contexts:
            context_summary = "\n\nSimilar pain points found:\n"
            for ctx in similar_contexts[:3]:
                context_summary += f"- {ctx.get('problem_statement', '')}\n"

        prompt = f"""Analyze this content and extract the core pain point.

Title: {content.get('title', '')}
Content: {content.get('body', '')}
Source: {content.get('metadata', {}).get('subreddit', 'unknown')}
{context_summary}

Focus on:
1. What is the REAL problem the user is facing?
2. How severe is this problem? (critical/high/medium/low)
3. Who is affected by this problem?
4. How frequently does this problem occur?
5. What makes this problem worth solving?

Provide your analysis in a structured format:
- Problem Statement: (1 sentence, clear and concise)
- Problem Detail: (2-3 sentences explaining context)
- Severity: (critical/high/medium/low with justification)
- Affected Users: (who experiences this problem)
- Frequency: (how often it occurs)
- Why It Matters: (business opportunity angle)

Be critical and honest - if there's no real pain point, say so.
"""

        analysis = self.think(prompt, temperature=0.5)
        logger.info(f"[{self.name}] Analysis complete")

        return {
            'raw_analysis': analysis,
            'agent': self.name
        }


class MarketResearcherAgent(BaseAgent):
    """시장 조사 및 경쟁 분석 전문 에이전트"""

    def __init__(self):
        super().__init__(
            name="Market Researcher",
            role="Market Analysis Specialist",
            expertise="Market sizing, competitive landscape, user willingness to pay, and business model validation"
        )

    def research_market(self, problem_analysis: str, pain_point: Dict) -> Dict:
        """
        Pain Point에 대한 시장 조사를 수행합니다.

        Args:
            problem_analysis: Problem Analyzer의 분석 결과
            pain_point: Pain Point 정보

        Returns:
            시장 조사 결과
        """
        logger.info(f"[{self.name}] Researching market for: {pain_point.get('problem_statement', '')[:50]}...")

        prompt = f"""Based on this pain point analysis, research the market opportunity.

Problem Analysis:
{problem_analysis}

Problem: {pain_point.get('problem_statement', '')}
Detail: {pain_point.get('problem_detail', '')}
Affected Users: {pain_point.get('affected_users', '')}

Provide market research insights:
1. Market Size: (niche/small/medium/large) with reasoning
2. Existing Solutions: List 3-5 existing tools/services that try to solve this
3. Solution Gaps: What are existing solutions missing?
4. Willingness to Pay: Would users pay for this? How much? (estimation)
5. Target Segments: Most valuable customer segments
6. Business Opportunity: Is this a viable business? Why/why not?

Be realistic and data-driven. Consider:
- Are there already too many solutions?
- Is the market saturated?
- Is the pain point valuable enough for monetization?
"""

        research = self.think(prompt, temperature=0.6)
        logger.info(f"[{self.name}] Research complete")

        return {
            'raw_research': research,
            'agent': self.name
        }


class SolutionDesignerAgent(BaseAgent):
    """혁신적인 솔루션 설계 전문 에이전트"""

    def __init__(self):
        super().__init__(
            name="Solution Designer",
            role="Solution Architecture Specialist",
            expertise="Product design, MVP definition, technical architecture, and go-to-market strategy"
        )

    def design_solution(
        self,
        problem_analysis: str,
        market_research: str,
        pain_point: Dict
    ) -> Dict:
        """
        Pain Point 해결을 위한 SaaS 솔루션을 설계합니다.

        Args:
            problem_analysis: Problem Analyzer의 분석
            market_research: Market Researcher의 조사
            pain_point: Pain Point 정보

        Returns:
            솔루션 설계 결과
        """
        logger.info(f"[{self.name}] Designing solution for: {pain_point.get('problem_statement', '')[:50]}...")

        prompt = f"""Design innovative SaaS solutions for this pain point.

Problem Analysis:
{problem_analysis}

Market Research:
{market_research}

Based on these insights, design 2-3 unique SaaS product ideas:

For each idea provide:
1. Title: Catchy, memorable name
2. Tagline: One sentence value proposition
3. Description: What it does and how it solves the problem (2-3 sentences)
4. Key Differentiators: What makes it unique vs existing solutions
5. MVP Features: 3-5 core features for launch
6. Tech Stack: Recommended technologies (be specific)
7. Business Model: subscription/freemium/one-time/usage-based with pricing
8. Target Audience: Specific customer persona
9. Go-to-Market: How to acquire first 100 customers
10. Estimated Dev Time: 1-2 months / 3-4 months / 6+ months
11. Complexity: simple/moderate/complex
12. Monthly Revenue Potential: Realistic estimate (e.g., $1k-5k, $10k-50k)

Focus on:
- Innovative approaches, not just "build X but better"
- Technical feasibility for indie hackers
- Clear path to monetization
- Differentiation from existing solutions

Output in JSON array format.
"""

        design = self.think(prompt, temperature=0.8)  # Higher creativity
        logger.info(f"[{self.name}] Solution design complete")

        return {
            'raw_design': design,
            'agent': self.name
        }


class QualityReviewerAgent(BaseAgent):
    """품질 검증 전문 에이전트"""

    def __init__(self):
        super().__init__(
            name="Quality Reviewer",
            role="Quality Assurance Specialist",
            expertise="Idea validation, feasibility assessment, and business viability scoring"
        )

    def review_solution(
        self,
        solution: Dict,
        problem_analysis: str,
        market_research: str
    ) -> Dict:
        """
        제안된 솔루션의 품질을 검증합니다.

        Args:
            solution: Solution Designer가 설계한 솔루션
            problem_analysis: Problem Analyzer의 분석
            market_research: Market Researcher의 조사

        Returns:
            품질 검증 결과
        """
        logger.info(f"[{self.name}] Reviewing solution: {solution.get('title', '')[:50]}...")

        prompt = f"""Review this SaaS idea critically and provide scores.

Proposed Solution:
Title: {solution.get('title', '')}
Description: {solution.get('description', '')}
MVP Features: {solution.get('mvp_features', [])}
Business Model: {solution.get('business_model', '')}

Original Analysis:
{problem_analysis[:500]}...

Market Context:
{market_research[:500]}...

Evaluate and score (0-10):

1. Feasibility Score (0-10):
   - Technical complexity
   - Time to market
   - Resource requirements
   Justification:

2. Market Score (0-10):
   - Market size
   - Competition level
   - Growth potential
   Justification:

3. Overall Score (0-10):
   - Average of above + bonus for innovation
   Justification:

4. Competition Level: low/medium/high
5. Key Risks: Top 3 risks
6. Success Probability: low/medium/high with reasoning

Be honest and critical. Not every idea deserves high scores.
Provide JSON output with scores and justifications.
"""

        review = self.think(prompt, temperature=0.3)  # Lower temperature for consistency
        logger.info(f"[{self.name}] Review complete")

        return {
            'raw_review': review,
            'agent': self.name
        }


class AgentCoordinator:
    """여러 에이전트의 작업을 조율하는 코디네이터"""

    def __init__(self):
        self.problem_analyzer = ProblemAnalyzerAgent()
        self.market_researcher = MarketResearcherAgent()
        self.solution_designer = SolutionDesignerAgent()
        self.quality_reviewer = QualityReviewerAgent()

    def analyze_with_agents(
        self,
        content: Dict,
        similar_contexts: List[Dict] = None
    ) -> Optional[Dict]:
        """
        여러 에이전트를 사용하여 콘텐츠를 분석하고 Pain Point를 추출합니다.

        Args:
            content: 분석할 콘텐츠
            similar_contexts: RAG 유사 컨텍스트

        Returns:
            Multi-agent 분석 결과 (Pain Point)
        """
        logger.info("=" * 60)
        logger.info("Multi-Agent Analysis Started")
        logger.info("=" * 60)

        try:
            # Step 1: Problem Analysis
            problem_result = self.problem_analyzer.analyze_content(content, similar_contexts)

            # Parse problem analysis to extract structured data
            pain_point = self._parse_problem_analysis(problem_result['raw_analysis'])

            if not pain_point or not pain_point.get('problem_statement'):
                logger.info("No valid pain point found by Problem Analyzer")
                return None

            # Step 2: Market Research
            market_result = self.market_researcher.research_market(
                problem_result['raw_analysis'],
                pain_point
            )

            # Enrich pain point with market insights
            market_insights = self._parse_market_research(market_result['raw_research'])
            pain_point.update(market_insights)

            logger.info("Multi-Agent Pain Point Analysis Complete")
            return pain_point

        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {e}", exc_info=True)
            return None

    def generate_ideas_with_agents(
        self,
        pain_point: Dict,
        problem_analysis: str,
        market_research: str
    ) -> List[Dict]:
        """
        여러 에이전트를 사용하여 SaaS 아이디어를 생성합니다.

        Args:
            pain_point: Pain Point 정보
            problem_analysis: Problem Analyzer의 원본 분석
            market_research: Market Researcher의 원본 조사

        Returns:
            검증된 SaaS 아이디어 목록
        """
        logger.info("=" * 60)
        logger.info("Multi-Agent Idea Generation Started")
        logger.info("=" * 60)

        try:
            # Step 1: Solution Design
            design_result = self.solution_designer.design_solution(
                problem_analysis,
                market_research,
                pain_point
            )

            # Parse solutions
            raw_solutions = self._parse_solutions(design_result['raw_design'])

            if not raw_solutions:
                logger.warning("No solutions generated")
                return []

            # Step 2: Quality Review for each solution
            validated_ideas = []
            for solution in raw_solutions:
                review_result = self.quality_reviewer.review_solution(
                    solution,
                    problem_analysis,
                    market_research
                )

                # Enrich solution with quality scores
                scores = self._parse_quality_review(review_result['raw_review'])
                solution.update(scores)

                # Add metadata
                solution['multi_agent_enhanced'] = True
                solution['agents_involved'] = [
                    self.problem_analyzer.name,
                    self.market_researcher.name,
                    self.solution_designer.name,
                    self.quality_reviewer.name
                ]

                validated_ideas.append(solution)

            logger.info(f"Multi-Agent Idea Generation Complete: {len(validated_ideas)} ideas")
            return validated_ideas

        except Exception as e:
            logger.error(f"Multi-agent idea generation failed: {e}", exc_info=True)
            return []

    def _parse_problem_analysis(self, raw_text: str) -> Dict:
        """Problem Analyzer의 텍스트 분석을 구조화된 데이터로 파싱"""
        # Simple keyword-based parsing
        lines = raw_text.split('\n')
        result = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Problem Statement:') or line.startswith('- Problem Statement:'):
                result['problem_statement'] = line.split(':', 1)[1].strip()
            elif line.startswith('Problem Detail:') or line.startswith('- Problem Detail:'):
                result['problem_detail'] = line.split(':', 1)[1].strip()
            elif line.startswith('Severity:') or line.startswith('- Severity:'):
                severity = line.split(':', 1)[1].strip().lower()
                if 'critical' in severity:
                    result['severity'] = 'critical'
                elif 'high' in severity:
                    result['severity'] = 'high'
                elif 'medium' in severity:
                    result['severity'] = 'medium'
                else:
                    result['severity'] = 'low'
            elif line.startswith('Affected Users:') or line.startswith('- Affected Users:'):
                result['affected_users'] = line.split(':', 1)[1].strip()
            elif line.startswith('Frequency:') or line.startswith('- Frequency:'):
                result['frequency'] = line.split(':', 1)[1].strip()

        return result

    def _parse_market_research(self, raw_text: str) -> Dict:
        """Market Researcher의 텍스트 조사를 구조화된 데이터로 파싱"""
        lines = raw_text.split('\n')
        result = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Market Size:') or line.startswith('1. Market Size:'):
                market_size = line.split(':', 1)[1].strip().lower()
                if 'large' in market_size:
                    result['market_size'] = 'large'
                elif 'medium' in market_size:
                    result['market_size'] = 'medium'
                elif 'small' in market_size:
                    result['market_size'] = 'small'
                else:
                    result['market_size'] = 'niche'
            elif line.startswith('Willingness to Pay:') or line.startswith('4. Willingness to Pay:'):
                result['willingness_to_pay'] = line.split(':', 1)[1].strip()

        return result

    def _parse_solutions(self, raw_text: str) -> List[Dict]:
        """Solution Designer의 텍스트를 JSON 솔루션 리스트로 파싱"""
        import json
        import re

        # Try to find JSON in the text
        json_match = re.search(r'\[[\s\S]*\]', raw_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                logger.warning("Failed to parse solution JSON, using fallback")

        # Fallback: return empty list
        return []

    def _parse_quality_review(self, raw_text: str) -> Dict:
        """Quality Reviewer의 텍스트 리뷰를 점수 딕셔너리로 파싱"""
        import json
        import re

        result = {
            'feasibility_score': 5,
            'market_score': 5,
            'overall_score': 5,
            'competition_level': 'medium'
        }

        # Try to find JSON
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            try:
                scores = json.loads(json_match.group())
                result.update(scores)
                return result
            except json.JSONDecodeError:
                pass

        # Fallback: regex parsing
        feasibility_match = re.search(r'Feasibility Score.*?(\d+)', raw_text, re.IGNORECASE)
        if feasibility_match:
            result['feasibility_score'] = int(feasibility_match.group(1))

        market_match = re.search(r'Market Score.*?(\d+)', raw_text, re.IGNORECASE)
        if market_match:
            result['market_score'] = int(market_match.group(1))

        overall_match = re.search(r'Overall Score.*?(\d+)', raw_text, re.IGNORECASE)
        if overall_match:
            result['overall_score'] = int(overall_match.group(1))

        competition_match = re.search(r'Competition Level:?\s*(low|medium|high)', raw_text, re.IGNORECASE)
        if competition_match:
            result['competition_level'] = competition_match.group(1).lower()

        return result
