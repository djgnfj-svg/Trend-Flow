# 데이터 포맷 정의서

## 1. 데이터베이스 스키마

### 1.1 sources 테이블 (트렌드 소스)
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100) NOT NULL UNIQUE    -- 'github_trending', 'product_hunt', etc.
category        VARCHAR(50)                     -- 'tech', 'general', 'startup'
url             TEXT
is_active       BOOLEAN DEFAULT TRUE
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### 1.2 trends 테이블 (원본 트렌드 데이터)
```sql
id                SERIAL PRIMARY KEY
source_id         INTEGER                       -- sources 테이블 참조
title             TEXT NOT NULL
description       TEXT
url               TEXT
category          VARCHAR(100)                  -- 원본 카테고리
rank              INTEGER                       -- 순위
metadata          JSONB                         -- 추가 메타데이터
collected_at      TIMESTAMP
collected_date    DATE                          -- 중복 방지용
created_at        TIMESTAMP
```

**metadata JSONB 예시 (GitHub Trending)**
```json
{
  "stars": 15000,
  "stars_today": 234,
  "forks": 1200,
  "language": "Python"
}
```

### 1.3 analyzed_trends 테이블 (AI 분석 결과)
```sql
id                  SERIAL PRIMARY KEY
trend_id            INTEGER                     -- trends 테이블 참조
summary             TEXT NOT NULL               -- AI 생성 요약
category            VARCHAR(100)                -- AI 분류 카테고리
problems            TEXT[]                      -- 문제점 배열
keywords            TEXT[]                      -- 키워드 배열
sentiment           VARCHAR(20)                 -- 'positive', 'neutral', 'negative'
importance_score    INTEGER (1-10)              -- 중요도 점수
analyzed_at         TIMESTAMP
created_at          TIMESTAMP
```

### 1.4 solutions 테이블 (솔루션 아이디어)
```sql
id                  SERIAL PRIMARY KEY
analyzed_trend_id   INTEGER                     -- analyzed_trends 테이블 참조
title               VARCHAR(255) NOT NULL
description         TEXT NOT NULL
feasibility         VARCHAR(20)                 -- 'high', 'medium', 'low'
estimated_effort    VARCHAR(20)                 -- '1주', '1개월', '3개월', '6개월'
target_audience     TEXT                        -- 타겟 사용자
tech_stack          TEXT[]                      -- 기술 스택 배열
created_at          TIMESTAMP
```

## 2. AI 분석 결과 JSON 포맷

### 2.1 트렌드 분석 결과
```json
{
  "summary": "트렌드의 핵심 내용을 1-2문장으로 요약",
  "category": "기술/비즈니스/사회/문화/경제 중 하나",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": ["이 트렌드가 해결하려는 문제점1", "문제점2"],
  "importance_score": 8,
  "sentiment": "positive/neutral/negative"
}
```

**필드 설명:**
- `summary` (string): 1-2문장 요약
- `category` (string): 기술, 비즈니스, 사회, 문화, 경제 중 택1
- `keywords` (array): 3-5개 키워드
- `problems` (array): 해결하려는 문제점들
- `importance_score` (integer): 1-10 사이 점수
- `sentiment` (string): positive, neutral, negative 중 택1

### 2.2 솔루션 아이디어 JSON
```json
{
  "solutions": [
    {
      "title": "솔루션 제목",
      "description": "솔루션에 대한 구체적인 설명 (2-3문장)",
      "feasibility": "high/medium/low",
      "estimated_effort": "1주/1개월/3개월/6개월",
      "target_audience": "타겟 사용자층",
      "tech_stack": ["기술1", "기술2", "기술3"]
    }
  ]
}
```

**필드 설명:**
- `title` (string): 솔루션 제목
- `description` (string): 구체적 설명 2-3문장
- `feasibility` (string): high, medium, low 중 택1
- `estimated_effort` (string): 예상 개발 기간
- `target_audience` (string): 누구를 위한 솔루션인지
- `tech_stack` (array): 추천 기술 스택

## 3. 크롤링 데이터 포맷

### 3.1 GitHub Trending
```python
{
    'title': 'owner/repository',
    'description': '레포지토리 설명',
    'url': 'https://github.com/owner/repository',
    'category': 'Python',  # 프로그래밍 언어
    'rank': 1,
    'metadata': {
        'stars': 15000,
        'stars_today': 234,
        'forks': 1200,
        'language': 'Python'
    }
}
```

### 3.2 Product Hunt (예정)
```python
{
    'title': '제품명',
    'description': '제품 설명',
    'url': 'https://www.producthunt.com/posts/product-name',
    'category': 'Productivity',
    'rank': 1,
    'metadata': {
        'upvotes': 523,
        'comments': 45,
        'maker': 'Maker Name'
    }
}
```

### 3.3 Google Trends (예정)
```python
{
    'title': '검색 키워드',
    'description': '트렌드 설명',
    'url': 'https://trends.google.com/...',
    'category': 'General',
    'rank': 1,
    'metadata': {
        'search_volume': 'high',
        'trend_direction': 'up',
        'region': 'KR'
    }
}
```

## 4. API 응답 포맷 (향후 구현 시)

### 4.1 GET /api/trends
```json
{
  "status": "success",
  "data": {
    "trends": [
      {
        "id": 1,
        "title": "트렌드 제목",
        "description": "설명",
        "source": "github_trending",
        "collected_at": "2025-11-12T10:00:00Z",
        "analysis": {
          "summary": "요약",
          "importance_score": 8,
          "sentiment": "positive"
        },
        "solutions_count": 3
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 10
  }
}
```

### 4.2 GET /api/trends/:id/solutions
```json
{
  "status": "success",
  "data": {
    "trend": {
      "id": 1,
      "title": "트렌드 제목"
    },
    "solutions": [
      {
        "id": 1,
        "title": "솔루션 제목",
        "description": "설명",
        "feasibility": "high",
        "estimated_effort": "3개월"
      }
    ]
  }
}
```

## 5. 데이터 제약사항

### 5.1 필수 필드
- **trends**: title (필수)
- **analyzed_trends**: summary (필수)
- **solutions**: title, description (필수)

### 5.2 값 제한
- `importance_score`: 1-10 사이 정수
- `sentiment`: 'positive', 'neutral', 'negative' 만 허용
- `feasibility`: 'high', 'medium', 'low' 만 허용

### 5.3 중복 방지
- 같은 소스에서 같은 날짜에 같은 제목의 트렌드는 중복 저장 안됨
- `UNIQUE(source_id, title, collected_date)`

## 6. 뷰 (View)

### 6.1 v_latest_trends
최신 트렌드 요약 정보 (JOIN된 데이터)

### 6.2 v_daily_stats
일별 수집/분석 통계

---

**작성일**: 2025-11-12
**버전**: 1.0
**관리**: database/schema.sql 참조
