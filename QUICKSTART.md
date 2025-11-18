# Pain Point Finder - Quick Start Guide

매우 실용적인 프로젝트로 재설계했습니다! 🎉

## 프로젝트 개요

**Reddit, Product Hunt, Indie Hackers**에서 실제 사용자의 Pain Point를 찾아내고, **Claude API + RAG**로 검증된 **SaaS/Micro Service 아이디어**를 자동 생성하는 시스템입니다.

### 핵심 기능
- ✅ 실제 사용자 문제점 자동 수집
- ✅ Claude API로 고품질 분석
- ✅ RAG로 과거 데이터 참조
- ✅ 시장 검증 자동화
- ✅ 비즈니스 모델 포함 아이디어 생성

---

## 빠른 시작 (5분)

### Step 1: API 키 발급

#### 1.1 Anthropic API Key (Claude AI) - **필수**
```bash
# 발급: https://console.anthropic.com/
# 회원가입 후 API Keys 메뉴에서 생성
# 비용: $5 크레딧 무료 제공
```

#### 1.2 OpenAI API Key (Embedding) - **필수**
```bash
# 발급: https://platform.openai.com/api-keys
# 비용: text-embedding-3-small - $0.02 / 1M tokens (거의 무료)
```

#### 1.3 Reddit API Credentials - **필수**
```bash
# 발급: https://www.reddit.com/prefs/apps
# 1. "create another app" 클릭
# 2. 이름: PainPointFinder
# 3. 타입: "script" 선택
# 4. redirect uri: http://localhost:8080
# 5. CLIENT_ID, CLIENT_SECRET 복사
```

#### 1.4 Product Hunt API Key - 선택
```bash
# 발급: https://api.producthunt.com/v2/oauth/applications
```

### Step 2: .env 파일 설정

`.env` 파일을 열어서 API 키를 입력하세요:

```bash
# 필수 API 키
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
REDDIT_CLIENT_ID=xxxxx
REDDIT_CLIENT_SECRET=xxxxx

# 선택 (Product Hunt)
PRODUCTHUNT_API_KEY=xxxxx
```

### Step 3: 프로토타입 테스트

Docker 없이 바로 테스트해볼 수 있습니다:

```bash
# 패키지 설치
pip install -r requirements.txt

# Reddit 수집기 테스트
python dags/collectors/reddit_collector.py

# Claude 분석기 테스트
python dags/ai_analysis/claude_analyzer.py
```

**예상 결과**:
```
[Reddit 수집기]
- r/SideProject에서 5개 포스트 수집
- Pain Point 키워드 필터링
- 댓글 포함 수집

[Claude 분석기]
- Pain Point 추출
- Confidence Score, Severity 계산
- SaaS 아이디어 3개 생성
- 비즈니스 모델, MVP, 가격 전략 포함
```

---

## 전체 시스템 실행

### Step 1: 데이터베이스 초기화

```bash
# Docker Compose 실행
docker compose up -d

# PostgreSQL에서 새 스키마 실행
docker compose exec postgres psql -U airflow -d airflow < database/schema_v2.sql

# pgvector 확장 설치 (선택)
docker compose exec postgres psql -U airflow -d airflow -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 테이블 확인
docker compose exec postgres psql -U airflow -d airflow -c "\dt"
```

### Step 2: ChromaDB 확인

```bash
# ChromaDB 컨테이너 상태 확인
docker compose ps chromadb

# ChromaDB 접속 테스트
curl http://localhost:8000/api/v1/heartbeat
```

### Step 3: 서비스 접속

- **Airflow UI**: http://localhost:8080 (airflow / airflow)
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001/docs
- **ChromaDB**: http://localhost:8000

---

## 워크플로우

### 전체 프로세스

```
1. Reddit 수집 (매일)
   ↓
2. 텍스트 전처리 & Embedding
   ↓
3. ChromaDB 저장
   ↓
4. Claude API: Pain Point 추출 (+ RAG 검색)
   ↓
5. Claude API: SaaS 아이디어 생성
   ↓
6. PostgreSQL 저장
   ↓
7. 프론트엔드에서 확인
```

### 데이터 흐름

```
Reddit/Product Hunt/Indie Hackers
         ↓
   raw_contents (PostgreSQL)
         ↓
   OpenAI Embedding
         ↓
   ChromaDB (Vector DB)
         ↓
   Claude API + RAG
         ↓
   pain_points (PostgreSQL)
         ↓
   Claude API
         ↓
   saas_ideas (PostgreSQL)
```

---

## 프로젝트 구조

```
Trend-Flow/
├── database/
│   ├── schema.sql                 # 기존 스키마
│   └── schema_v2.sql             # 새로운 스키마 ⭐
│
├── dags/
│   ├── collectors/
│   │   ├── reddit_collector.py   # Reddit 수집기 ⭐
│   │   ├── producthunt.py        # Product Hunt 수집기
│   │   └── indie_hackers.py      # Indie Hackers 크롤러 (TODO)
│   │
│   ├── ai_analysis/
│   │   ├── claude_analyzer.py    # Claude API 분석기 ⭐
│   │   └── rag_engine.py         # RAG 엔진 (TODO)
│   │
│   └── pain_point_pipeline_dag.py # 통합 DAG (TODO)
│
├── .env                           # API 키 설정 ⭐
├── requirements.txt               # 패키지 목록 ⭐
├── docker-compose.yaml            # Docker 설정 ⭐
├── PROJECT_PLAN_V2.md            # 상세 계획서 ⭐
└── QUICKSTART.md                 # 이 파일
```

---

## 다음 구현 단계

### Phase 1: 기본 플로우 (1주)

- [x] Reddit 수집기 (`reddit_collector.py`)
- [x] Claude 분석기 (`claude_analyzer.py`)
- [x] 데이터베이스 스키마 (`schema_v2.sql`)
- [ ] RAG 엔진 구현
- [ ] DB 저장 매니저 업데이트
- [ ] 통합 DAG 작성

### Phase 2: 추가 소스 (1주)

- [ ] Indie Hackers 크롤러
- [ ] Product Hunt 댓글 수집
- [ ] 데이터 전처리 최적화

### Phase 3: 시장 검증 (선택)

- [ ] Google Trends 연동
- [ ] 경쟁사 자동 검색
- [ ] 검증 점수 계산

### Phase 4: 프론트엔드 (1주)

- [ ] API 엔드포인트 추가
- [ ] Top 아이디어 대시보드
- [ ] Pain Point 필터링
- [ ] 상세 페이지

---

## 예상 비용

### 월간 운영 비용 (프로토타입)

| 항목 | 비용 | 설명 |
|------|------|------|
| Claude API | $30-100/월 | Pain Point 분석 + 아이디어 생성 |
| OpenAI Embedding | $1/월 | 임베딩 생성 (거의 무료) |
| ChromaDB | $0 | 로컬 Docker (무료) |
| Reddit API | $0 | 무료 |
| 인프라 | $0 | 로컬 Docker (무료) |
| **총합** | **$31-101/월** | 프로토타입 단계 |

### 비용 절감 팁

1. **Claude Haiku 사용**: 간단한 작업은 Haiku ($0.25/$1.25) 사용
2. **배치 처리**: API 호출 최소화
3. **캐싱**: 중복 분석 방지
4. **로컬 Embedding**: sentence-transformers (무료) 사용 가능

---

## 트러블슈팅

### 1. Claude API 오류

```
anthropic.AuthenticationError
```

**해결**: `.env` 파일의 `ANTHROPIC_API_KEY` 확인

```bash
# API 키 테스트
python -c "import anthropic; print(anthropic.Anthropic(api_key='your_key').models.list())"
```

### 2. Reddit API 오류

```
praw.exceptions.ResponseException: 401
```

**해결**: Reddit credentials 확인

```bash
# 테스트
python -c "import praw; r = praw.Reddit(client_id='xxx', client_secret='xxx', user_agent='test'); print(r.user.me())"
```

### 3. ChromaDB 연결 오류

```
ConnectionError: http://chromadb:8000
```

**해결**: ChromaDB 컨테이너 확인

```bash
docker compose ps chromadb
docker compose logs chromadb
```

### 4. PostgreSQL pgvector 오류

```
ERROR: type "vector" does not exist
```

**해결**: pgvector 확장 설치

```bash
docker compose exec postgres psql -U airflow -d airflow -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## 성공 지표

### 데이터 품질
- ✅ 일일 수집: 100+ 콘텐츠
- ✅ Pain Point 추출률: 20%+ (20개 이상)
- ✅ 아이디어 생성률: 100% (모든 Pain Point → 3개 아이디어)

### AI 품질
- ✅ Pain Point 신뢰도: 평균 0.8+
- ✅ 아이디어 실행 가능성: 평균 7+/10
- ✅ 시장 점수: 평균 6+/10

### 비즈니스 가치
- ✅ 실행 가능한 아이디어: 월 10개 이상
- ✅ 높은 점수 아이디어 (8+): 월 3개 이상

---

## 기술 스택

### 데이터 수집
- **Reddit**: PRAW (Python Reddit API Wrapper)
- **Product Hunt**: GraphQL API
- **Indie Hackers**: Selenium (웹 크롤링)

### AI & RAG
- **Claude API**: Anthropic (Pain Point 분석, 아이디어 생성)
- **OpenAI**: Embedding API (text-embedding-3-small)
- **ChromaDB**: Vector Database

### 백엔드
- **Apache Airflow**: 워크플로우 자동화
- **PostgreSQL**: 데이터 저장
- **pgvector**: Vector 검색
- **FastAPI**: API 서버

### 프론트엔드
- **React + Vite**: UI
- **TypeScript**: 타입 안전성
- **TailwindCSS**: 스타일링

---

## 다음 단계

### 1. 프로토타입 테스트

```bash
# Reddit 수집 테스트
python dags/collectors/reddit_collector.py

# Claude 분석 테스트
python dags/ai_analysis/claude_analyzer.py
```

### 2. 전체 플로우 구현

- RAG 엔진 작성
- DB 저장 로직 업데이트
- DAG 통합

### 3. 확장

- Indie Hackers 추가
- 시장 검증 자동화
- 프론트엔드 개발

---

## 추가 리소스

### 문서
- [PROJECT_PLAN_V2.md](./PROJECT_PLAN_V2.md) - 상세 프로젝트 계획
- [database/schema_v2.sql](./database/schema_v2.sql) - 데이터베이스 스키마

### API 문서
- [Claude API Docs](https://docs.anthropic.com/)
- [OpenAI Embedding Docs](https://platform.openai.com/docs/guides/embeddings)
- [Reddit API (PRAW)](https://praw.readthedocs.io/)
- [ChromaDB Docs](https://docs.trychroma.com/)

---

**프로젝트 시작할 준비 되셨나요?** 🚀

질문이 있으시면 언제든 물어보세요!
