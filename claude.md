# Apache Airflow 버전 정보

## 최신 버전
**Apache Airflow 3.1.2** (2025년 기준)

## 공식 문서
반드시 공식 문서를 확인하세요:
- 공식 문서: https://airflow.apache.org/docs/apache-airflow/stable/
- Docker Compose 가이드: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

## Docker Compose 다운로드

공식 docker-compose.yaml 파일 다운로드:
```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.1.2/docker-compose.yaml'
```

## 최소 요구사항
- Docker: 20.10.0 이상
- Docker Compose: v2.14.0 이상
- 메모리: 최소 4GB

## 기본 설정

### 1. 디렉토리 생성 (Linux)
```bash
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

### 2. 데이터베이스 초기화
```bash
docker compose up airflow-init
```

### 3. 서비스 시작
```bash
docker compose up
```

## 접속 정보
- Web UI: http://localhost:8080
- 기본 계정: airflow / airflow

## 주요 변경사항 (Airflow 3.x)
- 새로운 독립 컴포넌트: dag-processor, api-server
- 성능 개선 및 아키텍처 최적화
- Python 3.8+ 지원

## 코딩 가이드라인

### 1. 이모지 사용 금지
- 코드, 로그, 출력에서 절대 이모지 사용하지 않음
- 나쁜 예: print("✅ 저장 완료")
- 좋은 예: logger.info("저장 완료")

### 2. 로깅 규칙
- print() 사용 금지, logging 모듈 사용
- 로그 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL

### 3. 설정 관리
- 하드코딩 금지
- 환경변수 또는 설정 파일 사용
- 비밀번호, API 키 등은 반드시 환경변수로 관리

### 4. 매직 넘버 금지
- 상수는 파일 상단 또는 설정 파일에 정의
- 의미 있는 이름 사용

### 5. 더미 데이터 생성 절대 금지 ⚠️
- **절대로 테스트용 더미 데이터를 생성하지 마세요**
- 실제 API나 크롤링을 통해 진짜 데이터만 수집
- 나쁜 예: `generate_dummy_data()`, 하드코딩된 샘플 데이터
- 좋은 예: 실제 API 호출, 웹 크롤링
- API 키가 없거나 크롤링 실패 시: 에러를 발생시키고 명확히 안내

### 6. Docker 환경에서 테스트 필수 🐳
- **모든 테스트는 반드시 Docker Compose 환경에서 실행**
- 로컬 Python 환경 사용 금지 (의존성 차이로 인한 문제 방지)

```bash
# 잘못된 방법 ❌
python3 dags/collectors/something.py

# 올바른 방법 ✅
docker compose exec airflow-worker python /opt/airflow/dags/collectors/something.py
docker compose exec airflow-worker airflow dags test <dag_id> <date>
```

**주요 Docker 명령어:**
- Airflow 테스트: `docker compose exec airflow-worker <command>`
- Backend 테스트: `docker compose exec backend <command>`
- DB 접속: `docker compose exec postgres psql -U airflow -d airflow`

---

**중요**: 설정 전 반드시 공식 문서를 확인하여 최신 정보를 참고하세요.

---

# 프로젝트 현재 상태 및 구현 단계

## 전체 구현 단계

### 1단계: 데이터 가져오기 (매일)
- [ ] GitHub Search API로 트렌드 수집 (구현 필요)
- [ ] Product Hunt API로 트렌드 수집 (코드 작성됨, 검증 필요)

**필요한 API 키:**
- GITHUB_TOKEN (https://github.com/settings/tokens)
- PRODUCTHUNT_API_KEY (https://api.producthunt.com/v2/oauth/applications)

**검증 방법:**
```bash
# .env 파일에 API 키 추가
echo "GITHUB_TOKEN=your_token" >> .env
echo "PRODUCTHUNT_API_KEY=your_key" >> .env

# Docker 재시작
docker compose down && docker compose up -d

# Airflow DAG 테스트 실행
docker compose exec airflow-worker airflow dags test github_collection_and_analysis 2025-11-12
docker compose exec airflow-worker airflow dags test producthunt_collection_and_analysis 2025-11-12
```

**확인 사항:**
- 실제 API에서 데이터를 가져오는가?
- 에러 없이 완료되는가?
- 더미 데이터가 아닌가?

---

### 2단계: 데이터 DB에 넣기
- [ ] `trends` 테이블에 정상 저장 확인

**검증 방법:**
```bash
# DB 접속 후 데이터 확인
docker compose exec postgres psql -U airflow -d airflow

# 쿼리 실행
SELECT COUNT(*) FROM trends;
SELECT source_id, title, collected_at FROM trends ORDER BY collected_at DESC LIMIT 10;
```

**확인 사항:**
- 트렌드 데이터가 저장되는가?
- 중복 데이터가 없는가?
- source_id가 올바른가?

---

### 3단계: AI로 요약 + 요약 데이터 DB에 넣기

#### 매일 분석
- [ ] `analyzed_trends` 테이블에 분석 결과 저장 확인
- [ ] `solutions` 테이블에 솔루션 저장 확인

**검증 방법:**
```bash
# DB에서 분석 결과 확인
docker compose exec postgres psql -U airflow -d airflow

# 쿼리 실행
SELECT COUNT(*) FROM analyzed_trends;
SELECT COUNT(*) FROM solutions;
SELECT * FROM analyzed_trends ORDER BY analyzed_at DESC LIMIT 3;
```

**확인 사항:**
- Ollama AI가 실제로 분석을 수행하는가?
- 분석 결과가 의미있는가? (더미가 아닌가?)
- problems, keywords 필드가 채워지는가?

---

### 4단계: 프론트로 보여주기
- [ ] 트렌드 목록 페이지 동작 확인
- [ ] 분석 결과 표시 확인

**검증 방법:**
```bash
# Frontend/Backend 실행
npm run dev  # frontend 디렉토리에서
# Backend는 docker compose로 실행중

# 브라우저에서 확인
http://localhost:5173
```

**확인 사항:**
- API에서 데이터를 가져오는가?
- 화면에 제대로 표시되는가?
- 에러가 없는가?

---

## 현재 TASK 목록 (일단위 검증)

```
TASK 0: API 키 발급 및 설정
  └ GitHub Token 발급
  └ Product Hunt API Key 발급
  └ .env 파일에 추가

TASK 1: GitHub Search API로 수집기 구현
  └ 기존 크롤링 → GitHub Search API로 변경
  └ 최근 일주일간 스타 많이 받은 레포 검색
  └ DAG 실행 및 검증

TASK 2: Product Hunt 수집 검증
  └ DAG 실행해서 실제 데이터 수집되는지 확인
  └ DB에 저장되는지 확인

TASK 3: AI 분석 검증
  └ Ollama가 제대로 분석하는지 확인
  └ analyzed_trends, solutions 테이블 데이터 확인

TASK 4: 프론트엔드 동작 확인
  └ 브라우저에서 데이터가 보이는지 확인
  └ API 연결 확인
```

---

## 다음 단계
TASK 0부터 순서대로 진행
