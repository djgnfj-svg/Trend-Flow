"""
프로젝트 설정 파일
환경변수와 상수를 관리
"""
import os
from typing import Dict


# 데이터베이스 설정
DATABASE_CONFIG: Dict[str, any] = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'airflow'),
    'user': os.getenv('DB_USER', 'airflow'),
    'password': os.getenv('DB_PASSWORD', 'airflow'),
}

# Ollama AI 설정
OLLAMA_CONFIG: Dict[str, str] = {
    'host': os.getenv('OLLAMA_HOST', 'http://ollama:11434'),
    'model': os.getenv('OLLAMA_MODEL', 'qwen2.5:7b'),
}

# 크롤링 설정
CRAWLING_CONFIG: Dict[str, any] = {
    'github_trending_limit': int(os.getenv('GITHUB_LIMIT', '25')),
    'producthunt_limit': int(os.getenv('PRODUCTHUNT_LIMIT', '20')),
    'analyze_limit': int(os.getenv('ANALYZE_LIMIT', '10')),
    'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
    'user_agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
}

# 로깅 설정
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
