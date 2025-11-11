# Trend-Flow 시스템 아키텍처

## 🎯 프로젝트 목표
세상의 트렌드를 수집하고 AI로 분석하여 문제점과 솔루션 아이디어를 자동으로 제공하는 시스템

---

## 📊 전체 데이터 플로우

```
[트렌드 소스들]
    ↓ (크롤링/API)
[원본 데이터 수집]
    ↓ (정규화)
[PostgreSQL - trends 테이블]
    ↓ (전처리)
[로컬 AI (Ollama)]
    ↓ (분석 & 요약)
[PostgreSQL - analyzed_trends, solutions 테이블]
    ↓ (최종 결과)
[슬랙 알림 / 대시보드]
```

---

## 📥 1. 데이터 소스 (수집 대상)

### 한국 트렌드
| 소스 | 수집 방법 | 주기 | 우선순위 |
|------|----------|------|----------|
| **네이버 데이터랩** | 크롤링 (네이버 API 제한적) | 매일 | ⭐⭐⭐ |
| **Google Trends (한국)** | PyTrends 라이브러리 | 매일 | ⭐⭐⭐ |
| **네이버 실시간 검색어** | 크롤링 (RSS 가능) | 1시간 | ⭐⭐ |

### 글로벌 기술 트렌드
| 소스 | 수집 방법 | 주기 | 우선순위 |
|------|----------|------|----------|
| **GitHub Trending** | API / 크롤링 | 매일 | ⭐⭐⭐ |
| **Product Hunt** | 비공식 API / 크롤링 | 매일 | ⭐⭐⭐ |
| **Hacker News** | 공식 API | 매일 | ⭐⭐ |
| **Reddit (r/technology 등)** | Reddit API | 매일 | ⭐ |

### Phase 1 추천 (MVP)
**우선 구현:**
1. GitHub Trending (기술 트렌드, API 안정적)
2. Google Trends Korea (PyTrends 사용)
3. Product Hunt (스타트업/신제품 트렌드)

---

## 🗄️ 2. 데이터베이스 스키마

### 테이블 구조

#### `sources` - 트렌드 소스 관리
```sql
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,           -- 'github', 'product_hunt', 'google_trends'
    category VARCHAR(50),                 -- 'tech', 'general', 'startup'
    url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `trends` - 원본 트렌드 데이터
```sql
CREATE TABLE trends (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    category VARCHAR(100),                -- 카테고리
    rank INTEGER,                         -- 순위 (있는 경우)
    metadata JSONB,                       -- 추가 정보 (별 개수, 언어 등)
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_id, title, collected_at::DATE)  -- 중복 방지
);
```

#### `analyzed_trends` - AI 분석 결과
```sql
CREATE TABLE analyzed_trends (
    id SERIAL PRIMARY KEY,
    trend_id INTEGER REFERENCES trends(id),
    summary TEXT NOT NULL,                -- AI 생성 요약
    category VARCHAR(100),                -- AI가 분류한 카테고리
    problems TEXT[],                      -- 발견된 문제점들
    keywords TEXT[],                      -- 추출된 키워드
    sentiment VARCHAR(20),                -- 'positive', 'neutral', 'negative'
    importance_score INTEGER,             -- 1-10 중요도 점수
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `solutions` - 솔루션 아이디어
```sql
CREATE TABLE solutions (
    id SERIAL PRIMARY KEY,
    analyzed_trend_id INTEGER REFERENCES analyzed_trends(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    feasibility VARCHAR(20),              -- 'high', 'medium', 'low'
    estimated_effort VARCHAR(20),         -- '1주', '1개월', '3개월' 등
    target_audience TEXT,                 -- 타겟 사용자
    tech_stack TEXT[],                    -- 추천 기술 스택
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🤖 3. AI 분석 플로우

### 3단계 분석 프로세스

```
원본 트렌드 데이터
    ↓
[1단계: 요약 & 분류]
    - 트렌드 핵심 요약
    - 카테고리 자동 분류
    - 키워드 추출
    ↓
[2단계: 문제점 분석]
    - 어떤 문제를 해결하려는가?
    - 현재 한계점은?
    - 사용자 페인포인트는?
    ↓
[3단계: 솔루션 제안]
    - 구체적인 해결 방안
    - 실행 가능성 평가
    - 기술 스택 제안
```

### AI 프롬프트 예시

#### 1단계: 트렌드 분석
```python
ANALYSIS_PROMPT = """
다음 트렌드를 분석하고 JSON 형식으로 답변해주세요:

제목: {title}
설명: {description}
소스: {source}

다음 형식으로 답변:
{{
  "summary": "트렌드의 핵심을 1-2문장으로 요약",
  "category": "기술/비즈니스/사회/문화/경제 중 하나",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": [
    "이 트렌드가 해결하려는 문제점 1",
    "이 트렌드가 해결하려는 문제점 2"
  ],
  "importance_score": 1-10 사이의 중요도 점수,
  "sentiment": "positive/neutral/negative"
}}
"""
```

#### 2단계: 솔루션 생성
```python
SOLUTION_PROMPT = """
다음 트렌드와 문제점을 바탕으로 실행 가능한 솔루션 아이디어를 제안해주세요:

트렌드: {summary}
문제점: {problems}

3개의 솔루션 아이디어를 JSON 형식으로 제안:
{{
  "solutions": [
    {{
      "title": "솔루션 제목 (간결하게)",
      "description": "구체적인 솔루션 설명 (2-3문장)",
      "feasibility": "high/medium/low",
      "estimated_effort": "1주/1개월/3개월/6개월",
      "target_audience": "타겟 사용자층",
      "tech_stack": ["기술1", "기술2"]
    }}
  ]
}}
"""
```

---

## ⚙️ 4. Airflow DAG 구조

### 메인 DAG: `trend_analysis_pipeline`

```python
DAG 스케줄: 매일 오전 8시

Task 1: collect_github_trending
    ↓
Task 2: collect_product_hunt
    ↓
Task 3: collect_google_trends
    ↓
Task 4: normalize_and_save_to_db
    ↓
Task 5: ai_analyze_trends (병렬 처리 가능)
    ↓
Task 6: generate_solutions
    ↓
Task 7: calculate_importance_scores
    ↓
Task 8: send_slack_notification
```

### 보조 DAG들

- `cleanup_old_data_dag`: 30일 이상 된 데이터 정리 (주 1회)
- `model_health_check_dag`: AI 모델 상태 확인 (매일)
- `weekly_report_dag`: 주간 트렌드 리포트 생성 (주 1회)

---

## 🏗️ 5. 시스템 컴포넌트

### Docker Compose 서비스 구성

```yaml
services:
  # 기존
  - postgres (데이터베이스)
  - redis (Airflow 메시지 큐)
  - airflow-* (Airflow 서비스들)

  # 추가 필요
  - ollama (로컬 AI 모델)
  - adminer (DB 관리 도구, 선택사항)
```

### Python 패키지 구조

```
/dags
  /trend_collection
    __init__.py
    github_collector.py
    product_hunt_collector.py
    google_trends_collector.py
  /ai_analysis
    __init__.py
    analyzer.py
    prompt_templates.py
  /database
    __init__.py
    models.py
    schema.sql
  /utils
    __init__.py
    normalizer.py
    notifier.py
  trend_analysis_dag.py
```

---

## 📈 6. 최종 결과물 (Output)

### 슬랙 알림 형식
```
🔥 오늘의 트렌드 분석 (2025-11-11)

📊 수집된 트렌드: 25개
- GitHub: 10개
- Product Hunt: 8개
- Google Trends: 7개

⭐ Top 3 중요 트렌드:

1. [GitHub] AI Code Assistant 새 모델
   문제: 코드 자동완성의 정확도 한계
   💡 솔루션: 컨텍스트 인식 강화 모델 개발

2. [Product Hunt] 노코드 데이터 분석 툴
   문제: 비개발자의 데이터 접근성
   💡 솔루션: 자연어 기반 쿼리 인터페이스

...

📊 전체 리포트: http://dashboard.local/daily-report
```

### 데이터베이스 조회 예시
```sql
-- 오늘의 상위 10개 트렌드
SELECT
    t.title,
    s.name as source,
    at.summary,
    at.importance_score,
    COUNT(sol.id) as solution_count
FROM trends t
JOIN sources s ON t.source_id = s.id
JOIN analyzed_trends at ON at.trend_id = t.id
LEFT JOIN solutions sol ON sol.analyzed_trend_id = at.id
WHERE t.collected_at::DATE = CURRENT_DATE
ORDER BY at.importance_score DESC
LIMIT 10;
```

---

## 🚀 Phase 1 구현 순서 (MVP)

1. ✅ **Ollama 설정** - Qwen 2.5:7b 설치
2. ✅ **DB 스키마 생성** - 4개 테이블 생성
3. ✅ **GitHub Trending 크롤러** - 가장 쉽고 데이터 품질 좋음
4. ✅ **AI 분석 파이프라인** - 1개 소스로 먼저 테스트
5. ✅ **Airflow DAG** - 단순 버전으로 시작
6. ✅ **슬랙 알림** - 결과 확인
7. 🔄 **추가 소스** - Product Hunt, Google Trends 순차 추가

---

## 💡 다음 단계

어떤 것부터 시작할까요?

**Option 1**: Ollama + DB 스키마 먼저 (인프라 구축)
**Option 2**: GitHub 크롤러 먼저 (기능 검증)
**Option 3**: 전체를 한번에 구현

추천: **Option 1** → 기반을 튼튼하게 만든 후 기능 추가
