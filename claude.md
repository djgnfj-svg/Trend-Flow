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

---

**중요**: 설정 전 반드시 공식 문서를 확인하여 최신 정보를 참고하세요.
