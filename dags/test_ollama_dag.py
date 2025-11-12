from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import json


def test_ollama_connection():
    """Ollama 연결 테스트"""
    try:
        response = requests.get('http://ollama:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama 연결 성공!")
            print(f"설치된 모델: {models}")
            return models
        else:
            print(f"❌ Ollama 연결 실패: {response.status_code}")
            raise Exception("Ollama connection failed")
    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        raise


def test_ollama_chat():
    """Ollama 채팅 API 테스트"""
    try:
        url = 'http://ollama:11434/api/chat'

        payload = {
            "model": "qwen2.5:7b",
            "messages": [
                {
                    "role": "user",
                    "content": "안녕하세요! 간단하게 자기소개를 한 문장으로 해주세요."
                }
            ],
            "stream": False
        }

        print("🤖 Ollama에 메시지 전송 중...")
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            ai_message = result['message']['content']
            print(f"✅ AI 응답 성공!")
            print(f"📝 AI: {ai_message}")
            return ai_message
        else:
            print(f"❌ AI 응답 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            raise Exception("Ollama chat failed")

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        raise


def test_trend_analysis():
    """트렌드 분석 시뮬레이션"""
    try:
        url = 'http://ollama:11434/api/chat'

        trend_example = """
        제목: AI 코드 자동완성 도구의 새로운 모델 출시
        설명: GitHub에서 개발자들이 코드를 작성할 때 AI가 자동으로 완성해주는 도구의 새 버전이 출시되었습니다.
        정확도가 30% 향상되었고, 더 많은 프로그래밍 언어를 지원합니다.
        """

        payload = {
            "model": "qwen2.5:7b",
            "messages": [
                {
                    "role": "user",
                    "content": f"""다음 트렌드를 분석하고 JSON 형식으로 답변해주세요:

{trend_example}

다음 형식으로 답변:
{{
  "summary": "트렌드 핵심 요약 (1-2문장)",
  "category": "기술/비즈니스/사회/문화/경제 중 하나",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": ["해결하려는 문제점1", "해결하려는 문제점2"],
  "importance_score": 1-10,
  "sentiment": "positive/neutral/negative"
}}

JSON만 응답해주세요."""
                }
            ],
            "stream": False
        }

        print("🤖 트렌드 분석 중...")
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['message']['content']
            print(f"✅ 트렌드 분석 완료!")
            print(f"📊 분석 결과:\n{ai_response}")

            # JSON 파싱 시도
            try:
                # JSON 부분만 추출
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    analysis = json.loads(json_str)
                    print(f"✅ JSON 파싱 성공!")
                    print(f"요약: {analysis.get('summary')}")
                    print(f"중요도: {analysis.get('importance_score')}/10")
                    return analysis
            except Exception as parse_error:
                print(f"⚠️  JSON 파싱 실패 (응답은 받음): {str(parse_error)}")
                return ai_response

        else:
            print(f"❌ 트렌드 분석 실패: {response.status_code}")
            raise Exception("Trend analysis failed")

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        raise


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'test_ollama_api',
    default_args=default_args,
    description='Ollama AI API 연결 및 트렌드 분석 테스트',
    schedule=None,  # 수동 실행
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['test', 'ollama', 'ai'],
) as dag:

    # Task 1: Ollama 연결 테스트
    test_connection = PythonOperator(
        task_id='test_ollama_connection',
        python_callable=test_ollama_connection,
    )

    # Task 2: 간단한 채팅 테스트
    test_chat = PythonOperator(
        task_id='test_ollama_chat',
        python_callable=test_ollama_chat,
    )

    # Task 3: 트렌드 분석 시뮬레이션
    test_analysis = PythonOperator(
        task_id='test_trend_analysis',
        python_callable=test_trend_analysis,
    )

    # Task 순서 설정
    test_connection >> test_chat >> test_analysis
