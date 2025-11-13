# Trend-Flow 프로젝트 기획서

## 목표
매일 자동으로 트렌드를 수집하고 AI가 분석해서 실행 가능한 아이디어를 만들어주기

## 전체 흐름

```
매일 자동 실행:

1. 데이터 가져오기
   └ GitHub Trending, Product Hunt에서 트렌드 수집

2. DB에 저장
   └ PostgreSQL trends 테이블에 저장

3. AI 분석 + 저장
   └ Ollama AI로 분석 → analyzed_trends, solutions 테이블에 저장

4. 프론트에서 보기
   └ React 대시보드에서 결과 확인
```

## 데이터베이스 구조

### sources - 트렌드 소스 관리
```
id, name (github/product_hunt), category, url
```

### trends - 수집한 트렌드
```
id, source_id, title, description, url,
category, rank, metadata (JSON), collected_at
```

### analyzed_trends - AI 분석 결과
```
id, trend_id, summary, category,
problems (배열), keywords (배열),
sentiment, importance_score (1-10)
```

### solutions - 솔루션 아이디어
```
id, analyzed_trend_id, title, description,
feasibility, estimated_effort,
target_audience, tech_stack (배열)
```

## AI가 하는 일

### 단계 1: 트렌드 분석
입력: 트렌드 제목, 설명
출력: 요약, 카테고리, 키워드, 문제점, 중요도 점수

### 단계 2: 솔루션 생성
입력: 분석 결과
출력: 솔루션 3개 (제목, 설명, 실행 가능성, 예상 기간, 타겟, 기술스택)

## 현재 TASK

```
TASK 0: API 키 발급 및 설정
TASK 1: GitHub Search API로 수집기 구현
TASK 2: Product Hunt 수집 확인
TASK 3: AI 분석 확인
TASK 4: 프론트엔드 확인
```

## 기술 스택

### 백엔드
- Apache Airflow 3.1.2 (워크플로우 자동화)
- PostgreSQL (데이터 저장)
- Ollama + Qwen 2.5:7b (로컬 AI)
- FastAPI (API 서버)

### 프론트엔드
- React + Vite
- TypeScript

### 인프라
- Docker Compose
- Redis (Airflow 메시지 큐)

## 필요한 API 키

### 1. GitHub Token (필수)
**무료, 공식 API**
- Rate Limit: 시간당 60 요청 (인증 없이), 5,000 요청 (인증 시)

발급 방법:
1. https://github.com/settings/tokens 접속
2. "Generate new token" > "Classic" 선택
3. 권한: public_repo만 체크
4. 토큰 생성 후 복사
5. .env 파일에 추가:
   ```bash
   GITHUB_TOKEN=your_token_here
   ```

### 2. Product Hunt API Key (필수)
**무료, 비상업적 용도**
- Rate Limit: 15분당 6,250 복잡도 포인트

발급 방법:
1. https://www.producthunt.com/ 회원가입
2. https://api.producthunt.com/v2/oauth/applications 에서 앱 생성
3. API Key 복사
4. .env 파일에 추가:
   ```bash
   PRODUCTHUNT_API_KEY=your_key_here
   ```

## 실행 방법

### 1. 환경 설정
```bash
# .env 파일에 API 키 추가
echo "GITHUB_TOKEN=your_github_token" >> .env
echo "PRODUCTHUNT_API_KEY=your_producthunt_key" >> .env
```

### 2. Docker 실행
```bash
docker compose down
docker compose up -d
```

### 3. 접속
- Airflow: http://localhost:8080 (airflow / airflow)
- Frontend: http://localhost:5173

### 4. DAG 테스트
```bash
# GitHub 테스트
docker compose exec airflow-worker airflow dags test github_collection_and_analysis 2025-11-12

# Product Hunt 테스트
docker compose exec airflow-worker airflow dags test producthunt_collection_and_analysis 2025-11-12
```

### 5. DB 확인
```bash
docker compose exec postgres psql -U airflow -d airflow

# 트렌드 확인
SELECT COUNT(*) FROM trends;
SELECT * FROM trends ORDER BY collected_at DESC LIMIT 5;

# 분석 결과 확인
SELECT COUNT(*) FROM analyzed_trends;
SELECT * FROM analyzed_trends ORDER BY analyzed_at DESC LIMIT 3;
```

## 자동 실행 스케줄

- **GitHub**: 매일 오전 9시
- **Product Hunt**: 매일 오전 10시
