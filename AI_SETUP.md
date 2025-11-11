# 로컬 AI 설정 가이드

## 추천 방안

### 옵션 1: Ollama (추천) ⭐

**장점:**
- Docker로 쉽게 설정 가능
- 한국어 지원 모델 다수
- API 호출이 간단
- 무료 오픈소스

**추천 모델:**
1. **EXAONE 3.5** (LG AI Research) - 한국어 특화
2. **Qwen 2.5:7b** - 한국어 포함 29개 언어 지원
3. **Samsung TRM 13B** - 한국어 기업용, 메모리 최적화

---

## 빠른 시작 (Ollama)

### 1. Docker Compose에 Ollama 추가

`docker-compose.yaml`에 추가:

```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: trend-flow-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama-data:
```

### 2. 모델 설치

```bash
# 서비스 시작
docker compose up -d ollama

# 한국어 특화 모델 (추천)
docker exec -it trend-flow-ollama ollama pull exaone:7.8b

# 또는 다국어 모델
docker exec -it trend-flow-ollama ollama pull qwen2.5:7b-instruct

# 모델 확인
docker exec -it trend-flow-ollama ollama list
```

### 3. Python에서 사용

`requirements.txt`에 추가:
```
ollama-python>=0.1.0
```

사용 예시:
```python
import ollama

response = ollama.chat(
    model='exaone:7.8b',
    messages=[{
        'role': 'user',
        'content': '이 트렌드를 분석하고 문제점과 솔루션을 제안해줘: ...'
    }]
)
print(response['message']['content'])
```

---

## 하드웨어 요구사항

| 모델 크기 | 최소 RAM/VRAM |
|----------|---------------|
| 7B       | 8GB          |
| 13B      | 16GB         |
| 32B      | 32GB         |

**추천:** Qwen 2.5:7b (8GB RAM으로 충분)

---

## API 사용 예시

### 트렌드 분석 프롬프트

```python
def analyze_trend(trend_text):
    prompt = f"""
다음 트렌드를 분석하고 JSON 형식으로 답변해주세요:

트렌드: {trend_text}

다음 형식으로 답변:
{{
  "summary": "트렌드 요약 (한 문장)",
  "category": "카테고리 (기술/사회/경제/문화 등)",
  "problems": ["문제점1", "문제점2", "문제점3"],
  "solutions": [
    {{
      "title": "솔루션 제목",
      "description": "솔루션 설명",
      "feasibility": "높음/중간/낮음"
    }}
  ]
}}
"""

    response = ollama.chat(
        model='qwen2.5:7b-instruct',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return response['message']['content']
```

---

## 모델 선택 가이드

### 프로젝트 초기 (테스트)
- **Qwen 2.5:7b-instruct** (4.7GB)
- 빠르고 가볍고 한국어 지원 우수

### 프로덕션 (고품질 분석)
- **EXAONE 3.5:32b** (한국어 특화)
- 또는 **Qwen 2.5:14b**

### 메모리 제약이 있을 때
- **Samsung TRM 13B** (4-bit 양자화로 메모리 75% 절감)

---

## 다음 단계

1. ✅ docker-compose.yaml에 Ollama 추가
2. ✅ 모델 다운로드 (Qwen 2.5:7b 추천)
3. ✅ Python 라이브러리 설치 (ollama-python)
4. ✅ 간단한 테스트 스크립트 작성
5. ✅ Airflow DAG에 통합
