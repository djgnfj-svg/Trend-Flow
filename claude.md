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
