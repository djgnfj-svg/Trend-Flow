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
    'model': os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
}

# 크롤링 설정
CRAWLING_CONFIG: Dict[str, any] = {
    'github_trending_limit': int(os.getenv('GITHUB_LIMIT', '25')),
    'producthunt_limit': int(os.getenv('PRODUCTHUNT_LIMIT', '20')),
    'reddit_subreddits': os.getenv('REDDIT_SUBREDDITS', 'technology,programming,SideProject').split(','),
    'reddit_limit_per_subreddit': int(os.getenv('REDDIT_LIMIT_PER_SUBREDDIT', '10')),
    'analyze_limit': int(os.getenv('ANALYZE_LIMIT', '10')),
    'indie_hackers_limit': int(os.getenv('INDIE_HACKERS_LIMIT', '20')),
    'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
    'user_agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
}

# AI 분석 설정
AI_CONFIG: Dict[str, any] = {
    'use_multi_agent': os.getenv('USE_MULTI_AGENT', 'true').lower() == 'true',  # Multi-agent 활성화
    'anthropic_model': os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022'),
    'openai_embedding_model': os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'),
}

# 로깅 설정
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
