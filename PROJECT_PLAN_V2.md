# Pain Point Finder - 프로젝트 기획서 V2

## 목표
실제 사용자의 Pain Point를 자동으로 찾아내고, RAG를 활용하여 검증된 SaaS/Micro Service 아이디어를 생성하는 시스템

## 핵심 차별점

### 기존 프로젝트 (V1)
- GitHub Trending 수집
- 단순 트렌드 분석
- Ollama 로컬 AI

### 새로운 프로젝트 (V2)
- **실제 사용자 문제점 수집** (Reddit, Indie Hackers, Product Hunt)
- **Pain Point 중심 분석**
- **Claude API** (더 높은 품질)
- **RAG 시스템** (과거 데이터 참조)
- **시장 검증** (검색량, 경쟁사 분석)

---

## 전체 워크플로우

```
1. 데이터 수집 (매일 자동)
   ├─ Product Hunt: 새 제품, 사용자 피드백
   ├─ Reddit: 실제 불만과 문제점 (여러 Subreddit)
   └─ Indie Hackers: 인디 메이커들의 성공/실패 스토리

2. 전처리 & 임베딩
   ├─ 텍스트 정제 및 Chunking
   ├─ OpenAI Embedding API
   └─ Vector DB 저장 (ChromaDB)

3. Pain Point 추출 (Claude API + RAG)
   ├─ 유사 Pain Point 검색 (RAG)
   ├─ 컨텍스트와 함께 Claude API 호출
   └─ 구조화된 Pain Point 저장
      ├─ 문제 설명
      ├─ 영향받는 사용자
      ├─ 심각도, 빈도
      ├─ 시장 크기
      └─ 기존 솔루션 분석

4. SaaS 아이디어 생성 (Claude API)
   ├─ 비즈니스 모델 제안
   ├─ MVP 정의
   ├─ 기술 스택 추천
   ├─ 예상 개발 기간
   └─ 수익 예상

5. 시장 검증 (선택)
   ├─ Google Trends 검색량
   ├─ 경쟁사 분석
   └─ 검증 점수 계산

6. 프론트엔드에서 확인
   └─ Top 아이디어 대시보드
```

---

## 데이터 소스 상세

### 1. Product Hunt

**목적**: 새로운 제품의 문제 해결 방식 학습

**수집 데이터**:
- 제품 설명 (문제 정의)
- 사용자 댓글 (피드백, 불만)
- 투표 수, 토픽

**API**: Product Hunt GraphQL API (V2)

**예시 Pain Point**:
> "I'm tired of manually tracking my expenses across multiple apps"
> → Pain Point: 수동 지출 추적의 번거로움

---

### 2. Reddit

**목적**: 실제 사용자의 불만과 문제점 수집

**타겟 Subreddit** (우선순위순):

| Subreddit | 목적 | 예상 Pain Point |
|-----------|------|----------------|
| r/SideProject | 사이드 프로젝트 아이디어 | "I need X but can't find a good tool" |
| r/Entrepreneur | 창업자들의 고민 | 비즈니스 운영 문제 |
| r/startups | 스타트업 문제 | 마케팅, 채용, 자금 조달 |
| r/SaaS | SaaS 피드백 | 기능 요청, 가격 불만 |
| r/webdev | 개발자 도구 | 개발 도구의 부족함 |
| r/smallbusiness | 소상공인 | 회계, 재고 관리 문제 |
| r/freelance | 프리랜서 | 프로젝트 관리, 계약 |

**수집 방법**: Reddit API (PRAW 라이브러리)

**수집 기준**:
- 최근 7일 내 게시글
- Upvote 10개 이상
- 키워드: "pain", "problem", "frustrated", "wish there was", "need", "struggle"

**예시**:
```
Title: "I'm spending 5 hours a week on invoicing. There has to be a better way"
Body: "I run a small consulting business and manually create invoices in Excel..."
→ Pain Point: 소규모 컨설턴트의 수동 청구서 작성
```

---

### 3. Indie Hackers

**목적**: 인디 메이커들의 실제 경험 수집

**수집 대상**:
- 성공 스토리 포스트
- 실패 분석 포스트
- 댓글 (사용자 피드백)
- 제품 페이지

**수집 방법**: 웹 크롤링 (Selenium/BeautifulSoup)
- URL: https://www.indiehackers.com/forum
- 섹션: Popular, New, Ask IH

**수집 기준**:
- 최근 7일 내 게시글
- 댓글 5개 이상

**예시**:
```
Post: "Why my SaaS failed after 6 months"
"Users loved the idea but the onboarding was too complex..."
→ Pain Point: 복잡한 온보딩 프로세스
```

---

## AI 시스템: Claude API + RAG

### Claude API 통합

#### 사용 모델
- **Claude 3.5 Sonnet**: Pain Point 분석, 아이디어 생성
- **Claude 3 Haiku**: 간단한 분류, 텍스트 정제

#### API 설정
```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    temperature=0.7,
    messages=[...]
)
```

#### 비용 예상 (Claude 3.5 Sonnet)
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**일일 예상 비용**:
- 수집 데이터: 200개 포스트/댓글
- 평균 토큰: 500 input + 1000 output
- 일일 비용: (200 * 500 * $3 / 1M) + (200 * 1000 * $15 / 1M) = $0.30 + $3.00 = **$3.30/일**
- 월 비용: **약 $100/월**

---

### RAG 시스템 설계

#### 1. Vector Database: ChromaDB

**선택 이유**:
- 오픈소스, 무료
- Python 통합 간편
- Docker로 실행 가능
- 로컬 개발 용이

**설치 및 실행**:
```bash
# Docker로 실행
docker run -p 8000:8000 chromadb/chroma

# Python 클라이언트
pip install chromadb
```

**대안**:
- **Pinecone**: 클라우드, 프리티어 100K 벡터
- **Weaviate**: 오픈소스, GraphQL 지원
- **PostgreSQL + pgvector**: 기존 DB 활용

#### 2. Embedding 모델: OpenAI

**text-embedding-3-small**
- 1536 차원
- 비용: $0.02 / 1M tokens
- 한글 지원 우수

**비용 예상**:
- 일일 200개 * 평균 300 토큰 = 60K tokens
- 일일 비용: $0.02 * 0.06 = **$0.0012/일** (거의 무료)

**대안**:
- **sentence-transformers** (무료, 로컬)
- **Cohere Embed** ($0.10 / 1M tokens)

#### 3. RAG 워크플로우

```python
# 1. 새로운 콘텐츠 수집
content = fetch_reddit_post()

# 2. 임베딩 생성
embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=content.text
)

# 3. ChromaDB에 저장
collection.add(
    documents=[content.text],
    embeddings=[embedding.data[0].embedding],
    metadatas=[{"source": "reddit", "id": content.id}],
    ids=[content.id]
)

# 4. 유사 Pain Point 검색
results = collection.query(
    query_embeddings=[embedding.data[0].embedding],
    n_results=5
)

# 5. Claude API에 컨텍스트와 함께 전달
context = "\n".join([r for r in results['documents'][0]])
prompt = f"""
다음은 유사한 Pain Point들입니다:
{context}

새로운 콘텐츠를 분석하여 Pain Point를 추출하세요:
{content.text}
"""

response = claude.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": prompt}]
)
```

---

## Pain Point 분석 프롬프트

### 단계 1: Pain Point 추출

```
당신은 SaaS 아이디어 발굴 전문가입니다.

다음 콘텐츠를 분석하여 **실제 사용자의 Pain Point**를 추출하세요.

<유사한 과거 Pain Point들>
{similar_pain_points}
</유사한 과거 Pain Point들>

<분석할 콘텐츠>
제목: {title}
본문: {body}
출처: {source}
</분석할 콘텐츠>

다음 형식의 JSON으로 응답하세요:

{
  "has_pain_point": true/false,
  "problem_statement": "한 문장으로 문제 요약",
  "problem_detail": "상세 설명",
  "affected_users": "영향받는 사용자 (예: 프리랜서, 소상공인)",
  "frequency": "daily/weekly/monthly/occasional",
  "severity": "critical/high/medium/low",
  "market_size": "large/medium/small/niche",
  "willingness_to_pay": "high/medium/low/unknown",
  "existing_solutions": ["기존 솔루션1", "기존 솔루션2"],
  "solution_gaps": "기존 솔루션이 해결하지 못하는 점",
  "keywords": ["키워드1", "키워드2"],
  "category": "productivity/finance/communication/etc",
  "confidence_score": 0.85
}

**판단 기준**:
1. 명확한 문제가 있는가?
2. 해결할 가치가 있는가?
3. 여러 사람이 겪는 문제인가?
4. 기술적으로 해결 가능한가?
```

### 단계 2: SaaS 아이디어 생성

```
다음 Pain Point를 해결하는 **구체적인 SaaS/Micro Service 아이디어**를 3개 생성하세요.

<Pain Point>
{pain_point_json}
</Pain Point>

<유사 제품들>
{similar_products}
</유사 제품들>

각 아이디어는 다음 형식의 JSON으로 응답하세요:

{
  "ideas": [
    {
      "title": "서비스 이름",
      "tagline": "한 줄 설명 (10단어 이내)",
      "description": "상세 설명 (3-5문장)",
      "business_model": "subscription/freemium/one-time/usage-based",
      "pricing_model": "구체적인 가격 전략",
      "estimated_monthly_revenue": "$0-$1K/$1K-$10K/$10K-$50K/$50K+",
      "tech_stack": ["React", "Node.js", "PostgreSQL"],
      "complexity": "simple/moderate/complex",
      "estimated_dev_time": "1주/1개월/3개월/6개월+",
      "mvp_features": [
        "핵심 기능 1",
        "핵심 기능 2",
        "핵심 기능 3"
      ],
      "mvp_description": "MVP 설명 (2-3문장)",
      "target_audience": "타겟 고객 상세",
      "go_to_market_strategy": "어떻게 고객을 확보할 것인가",
      "competition_level": "low/medium/high",
      "differentiation": "기존 솔루션과 차별점",
      "feasibility_score": 8,
      "market_score": 7,
      "overall_score": 8,
      "tags": ["tag1", "tag2"],
      "similar_products": ["Notion", "Airtable"]
    }
  ]
}

**요구사항**:
1. 각 아이디어는 서로 다른 접근 방식
2. 최소 1개는 simple complexity
3. MVP는 1-3개월 내 개발 가능한 범위
4. 실제 비즈니스 모델 포함
5. 경쟁사 대비 명확한 차별점
```

---

## 구현 우선순위

### Phase 1: 기본 인프라 (1-2주)

#### TASK 1.1: API 키 설정
- [ ] Anthropic API Key 발급 (https://console.anthropic.com/)
- [ ] OpenAI API Key 발급 (Embedding용)
- [ ] Reddit API 키 발급
- [ ] Product Hunt API 키 (기존 사용)

#### TASK 1.2: 데이터베이스 마이그레이션
- [ ] schema_v2.sql 실행
- [ ] pgvector 확장 설치 (선택)
- [ ] 기존 데이터 백업

#### TASK 1.3: ChromaDB 셋업
- [ ] Docker로 ChromaDB 실행
- [ ] Python 클라이언트 테스트
- [ ] Collection 생성

---

### Phase 2: 데이터 수집기 (1주)

#### TASK 2.1: Reddit 수집기 구현
- [ ] PRAW 라이브러리 설치
- [ ] Subreddit 리스트 설정
- [ ] 포스트 + 댓글 수집
- [ ] raw_contents 테이블 저장
- [ ] DAG 작성

#### TASK 2.2: Indie Hackers 크롤러
- [ ] Selenium 설정
- [ ] 포스트 크롤링
- [ ] 댓글 수집
- [ ] raw_contents 저장
- [ ] DAG 작성

#### TASK 2.3: Product Hunt 수집기 수정
- [ ] 댓글 수집 추가
- [ ] raw_contents 테이블로 변경

---

### Phase 3: AI 분석 파이프라인 (1-2주)

#### TASK 3.1: Embedding 생성
- [ ] OpenAI Embedding API 통합
- [ ] 텍스트 전처리 (정제, Chunking)
- [ ] ChromaDB 저장
- [ ] embeddings 테이블 저장 (백업용)

#### TASK 3.2: Pain Point 추출
- [ ] Claude API 클라이언트 작성
- [ ] RAG 검색 로직 구현
- [ ] Pain Point 추출 프롬프트 작성
- [ ] JSON 파싱 및 검증
- [ ] pain_points 테이블 저장

#### TASK 3.3: SaaS 아이디어 생성
- [ ] 아이디어 생성 프롬프트 작성
- [ ] Claude API 호출
- [ ] saas_ideas 테이블 저장

#### TASK 3.4: DAG 통합
- [ ] 전체 파이프라인 DAG 작성
- [ ] 에러 핸들링
- [ ] 로깅

---

### Phase 4: 시장 검증 (선택, 1주)

#### TASK 4.1: Google Trends 연동
- [ ] pytrends 라이브러리 사용
- [ ] 검색량 수집

#### TASK 4.2: 경쟁사 분석
- [ ] 구글 검색 자동화
- [ ] 경쟁사 수집
- [ ] 가격 정보 크롤링

#### TASK 4.3: 검증 점수 계산
- [ ] 검증 알고리즘 작성
- [ ] market_validation 테이블 저장

---

### Phase 5: 프론트엔드 (1주)

#### TASK 5.1: API 엔드포인트
- [ ] `/api/pain-points` - Pain Point 목록
- [ ] `/api/saas-ideas` - 아이디어 목록
- [ ] `/api/top-ideas` - Top 아이디어
- [ ] `/api/stats` - 통계

#### TASK 5.2: 대시보드 UI
- [ ] Top 아이디어 카드
- [ ] Pain Point 필터링
- [ ] 상세 페이지
- [ ] 통계 차트

---

## 예상 비용

### 월간 비용 (100% 가동 시)

| 항목 | 비용 | 설명 |
|------|------|------|
| Claude API | $100/월 | Pain Point 분석 + 아이디어 생성 |
| OpenAI Embedding | $1/월 | 임베딩 생성 (거의 무료) |
| ChromaDB | $0 | 로컬 또는 Docker (무료) |
| Reddit API | $0 | 무료 |
| 인프라 (선택) | $10-50/월 | VPS, 도메인 (선택) |
| **총합** | **$111-151/월** | 프로토타입은 $100/월로 가능 |

### 비용 절감 방법
1. **Claude Haiku 사용**: 간단한 작업은 Haiku ($0.25/$1.25)
2. **배치 처리**: API 호출 횟수 최소화
3. **캐싱**: 중복 분석 방지
4. **로컬 Embedding**: sentence-transformers 사용 (무료)

---

## 기술 스택 요약

### 백엔드
- Apache Airflow 3.1.2 (워크플로우)
- PostgreSQL + pgvector (데이터 + 벡터 검색)
- ChromaDB (Vector Database)
- Claude API (AI 분석)
- OpenAI Embedding API (임베딩)
- FastAPI (API 서버)
- PRAW (Reddit API)
- Selenium (Indie Hackers 크롤링)

### 프론트엔드
- React + Vite
- TypeScript
- TailwindCSS

### 인프라
- Docker Compose
- Redis (Airflow 메시지 큐)

---

## 성공 지표

### 데이터 품질
- 일일 수집: 100+ 콘텐츠
- Pain Point 추출률: 20%+ (20개 이상)
- 아이디어 생성률: 100% (모든 Pain Point → 3개 아이디어)

### AI 품질
- Pain Point 신뢰도: 평균 0.8+
- 아이디어 실행 가능성: 평균 7+/10
- 시장 검증 점수: 평균 6+/10

### 비즈니스 가치
- 실행 가능한 아이디어: 월 10개 이상
- 높은 점수 아이디어 (8+): 월 3개 이상

---

## 다음 단계

1. **API 키 발급**
   - Anthropic API Key
   - OpenAI API Key
   - Reddit API Credentials

2. **프로토타입 구현**
   - Reddit 수집기 1개 구현
   - Claude API 통합
   - Pain Point 1개 추출 테스트

3. **검증**
   - 수집 → 분석 → 아이디어 전체 플로우 1회 실행
   - 품질 확인

4. **확장**
   - 나머지 소스 추가
   - RAG 최적화
   - 프론트엔드 개발

---

**시작할 준비가 되셨나요?**

다음 작업을 진행하겠습니다:
1. `.env` 파일에 새로운 API 키 추가
2. `requirements.txt` 업데이트 (Claude SDK, PRAW, ChromaDB 등)
3. Reddit 수집기 프로토타입 작성
4. Claude API 통합 테스트
