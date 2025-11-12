#!/usr/bin/env python3
"""
Ollama API 테스트 스크립트
"""
import requests
import json


def test_connection():
    """Ollama 연결 테스트"""
    print("=" * 50)
    print("🔍 1. Ollama 연결 테스트")
    print("=" * 50)
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama 연결 성공!")
            print(f"📦 설치된 모델:")
            for model in models.get('models', []):
                print(f"  - {model['name']} ({model['size'] / 1e9:.1f} GB)")
            return True
        else:
            print(f"❌ 연결 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return False


def test_simple_chat():
    """간단한 채팅 테스트"""
    print("\n" + "=" * 50)
    print("💬 2. 간단한 채팅 테스트")
    print("=" * 50)
    try:
        url = 'http://localhost:11434/api/chat'
        payload = {
            "model": "llama3.2:3b",
            "messages": [
                {
                    "role": "user",
                    "content": "안녕하세요! 당신은 누구인가요? 한 문장으로 답변해주세요."
                }
            ],
            "stream": False
        }

        print("🤖 AI에게 메시지 전송 중...")
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            ai_message = result['message']['content']
            print(f"✅ AI 응답 성공!")
            print(f"📝 AI: {ai_message}")
            return True
        else:
            print(f"❌ 응답 실패: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return False


def test_trend_analysis():
    """트렌드 분석 테스트"""
    print("\n" + "=" * 50)
    print("📊 3. 트렌드 분석 테스트")
    print("=" * 50)
    try:
        url = 'http://localhost:11434/api/chat'

        trend_example = """
제목: AI 코드 자동완성 도구의 새로운 모델 출시
설명: GitHub에서 개발자들이 코드를 작성할 때 AI가 자동으로 완성해주는
도구의 새 버전이 출시되었습니다. 정확도가 30% 향상되었고,
더 많은 프로그래밍 언어를 지원합니다.
        """

        payload = {
            "model": "llama3.2:3b",
            "messages": [
                {
                    "role": "user",
                    "content": f"""다음 트렌드를 분석하고 JSON 형식으로만 답변해주세요:

{trend_example}

{{
  "summary": "트렌드 핵심 요약 (1-2문장)",
  "category": "기술/비즈니스/사회/문화/경제",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "problems": ["문제점1", "문제점2"],
  "importance_score": 8,
  "sentiment": "positive"
}}

위 형식의 JSON만 응답하세요."""
                }
            ],
            "stream": False
        }

        print("🤖 트렌드 분석 중... (시간이 좀 걸릴 수 있습니다)")
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['message']['content']
            print(f"✅ AI 분석 완료!")
            print(f"\n📄 원본 응답:")
            print(ai_response)

            # JSON 파싱 시도
            try:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    analysis = json.loads(json_str)
                    print(f"\n✅ JSON 파싱 성공!")
                    print(f"\n📊 분석 결과:")
                    print(f"  - 요약: {analysis.get('summary')}")
                    print(f"  - 카테고리: {analysis.get('category')}")
                    print(f"  - 키워드: {', '.join(analysis.get('keywords', []))}")
                    print(f"  - 중요도: {analysis.get('importance_score')}/10")
                    print(f"  - 감정: {analysis.get('sentiment')}")
                    return True
            except Exception as parse_error:
                print(f"\n⚠️  JSON 파싱 실패: {str(parse_error)}")
                print("하지만 AI 응답은 정상적으로 받았습니다.")
                return True

        else:
            print(f"❌ 분석 실패: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🚀 Ollama API 테스트 시작\n")

    results = []

    # 1. 연결 테스트
    results.append(("연결 테스트", test_connection()))

    # 2. 간단한 채팅
    results.append(("채팅 테스트", test_simple_chat()))

    # 3. 트렌드 분석
    results.append(("트렌드 분석", test_trend_analysis()))

    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약")
    print("=" * 50)
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")

    total_success = sum(1 for _, success in results if success)
    print(f"\n총 {total_success}/{len(results)} 테스트 성공")

    if total_success == len(results):
        print("\n🎉 모든 테스트 통과! Ollama가 정상 작동합니다.")
    else:
        print("\n⚠️  일부 테스트 실패. 로그를 확인하세요.")
