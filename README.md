# Trend-Flow

매일 자동으로 트렌드를 수집하고 AI가 분석해서 아이디어를 만들어주는 프로젝트

## 빠른 시작

```bash
# 1. API 키 설정
echo "GITHUB_TOKEN=your_github_token" >> .env
echo "PRODUCTHUNT_API_KEY=your_producthunt_key" >> .env

# 2. Docker 실행
docker compose down && docker compose up -d

# 3. 접속
# Airflow: http://localhost:8080 (airflow/airflow)
# Frontend: http://localhost:5173
```

## 기술 스택
Apache Airflow · Ollama AI · PostgreSQL · React · FastAPI

## 자세한 내용
**[PROJECT_PLAN.md](./PROJECT_PLAN.md)** 참고