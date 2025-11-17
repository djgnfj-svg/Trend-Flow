"""
RAG Engine - ChromaDB를 사용한 Vector 검색
과거 Pain Point를 참조하여 더 정확한 분석 제공
"""
import chromadb
from chromadb.config import Settings
import openai
import os
import logging
from typing import List, Dict, Optional
import json

# 로거 설정
logger = logging.getLogger(__name__)

# API 키 및 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
CHROMADB_HOST = os.getenv('CHROMADB_HOST', 'localhost')
CHROMADB_PORT = int(os.getenv('CHROMADB_PORT', '8000'))
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
EMBEDDING_DIMENSIONS = int(os.getenv('EMBEDDING_DIMENSIONS', '1536'))


class RAGEngine:
    """RAG 엔진 - Vector DB 기반 유사 검색"""

    def __init__(self):
        """초기화"""
        if not OPENAI_API_KEY:
            error_msg = (
                "OpenAI API Key가 설정되지 않았습니다.\n"
                "환경변수 OPENAI_API_KEY를 설정해주세요.\n"
                "발급: https://platform.openai.com/api-keys"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # OpenAI 클라이언트
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # ChromaDB 클라이언트
        try:
            self.chroma_client = chromadb.HttpClient(
                host=CHROMADB_HOST,
                port=CHROMADB_PORT,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            # 연결 테스트
            self.chroma_client.heartbeat()
            logger.info(f"ChromaDB 연결 성공 ({CHROMADB_HOST}:{CHROMADB_PORT})")

        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {str(e)}")
            logger.error("Docker로 ChromaDB를 실행하세요: docker compose up chromadb -d")
            raise

        # 컬렉션 초기화
        self.pain_points_collection = self._get_or_create_collection('pain_points')
        self.raw_contents_collection = self._get_or_create_collection('raw_contents')

        logger.info("RAG Engine 초기화 완료")

    def _get_or_create_collection(self, name: str):
        """컬렉션 가져오기 또는 생성"""
        try:
            collection = self.chroma_client.get_collection(name=name)
            logger.info(f"컬렉션 '{name}' 로드 완료 (문서 수: {collection.count()})")
        except Exception:
            collection = self.chroma_client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}  # 코사인 유사도 사용
            )
            logger.info(f"컬렉션 '{name}' 생성 완료")

        return collection

    def create_embedding(self, text: str) -> List[float]:
        """
        텍스트를 Vector Embedding으로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            Vector embedding (1536 차원)
        """
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Embedding 생성 완료 (길이: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Embedding 생성 실패: {str(e)}")
            raise

    def add_raw_content(
        self,
        content_id: int,
        title: str,
        body: str,
        metadata: Dict
    ) -> bool:
        """
        원본 콘텐츠를 Vector DB에 추가

        Args:
            content_id: raw_contents 테이블의 ID
            title: 제목
            body: 본문
            metadata: 추가 메타데이터

        Returns:
            성공 여부
        """
        try:
            # 텍스트 결합
            full_text = f"{title}\n\n{body}"

            # Embedding 생성
            embedding = self.create_embedding(full_text)

            # ChromaDB에 저장
            self.raw_contents_collection.add(
                ids=[str(content_id)],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[metadata]
            )

            logger.info(f"원본 콘텐츠 추가 완료 (ID: {content_id})")
            return True

        except Exception as e:
            logger.error(f"원본 콘텐츠 추가 실패: {str(e)}")
            return False

    def add_pain_point(
        self,
        pain_point_id: int,
        problem_statement: str,
        problem_detail: str,
        metadata: Dict
    ) -> bool:
        """
        Pain Point를 Vector DB에 추가

        Args:
            pain_point_id: pain_points 테이블의 ID
            problem_statement: 문제 요약
            problem_detail: 문제 상세
            metadata: 추가 메타데이터 (affected_users, severity, etc.)

        Returns:
            성공 여부
        """
        try:
            # 텍스트 결합
            full_text = f"{problem_statement}\n\n{problem_detail}"

            # Embedding 생성
            embedding = self.create_embedding(full_text)

            # ChromaDB에 저장
            self.pain_points_collection.add(
                ids=[str(pain_point_id)],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[metadata]
            )

            logger.info(f"Pain Point 추가 완료 (ID: {pain_point_id})")
            return True

        except Exception as e:
            logger.error(f"Pain Point 추가 실패: {str(e)}")
            return False

    def search_similar_pain_points(
        self,
        query_text: str,
        n_results: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        유사한 Pain Point 검색

        Args:
            query_text: 검색할 텍스트
            n_results: 반환할 최대 결과 수
            min_similarity: 최소 유사도 (0.0 ~ 1.0)

        Returns:
            유사한 Pain Point 목록
        """
        try:
            # Embedding 생성
            query_embedding = self.create_embedding(query_text)

            # 검색
            results = self.pain_points_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # 결과 파싱
            similar_points = []

            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    # 거리를 유사도로 변환 (코사인 거리 → 코사인 유사도)
                    distance = results['distances'][0][i]
                    similarity = 1 - distance

                    # 최소 유사도 필터링
                    if similarity < min_similarity:
                        continue

                    similar_point = {
                        'id': results['ids'][0][i],
                        'problem_statement': results['documents'][0][i].split('\n\n')[0],
                        'similarity': round(similarity, 3),
                        'metadata': results['metadatas'][0][i]
                    }
                    similar_points.append(similar_point)

            logger.info(f"유사 Pain Point {len(similar_points)}개 발견")

            return similar_points

        except Exception as e:
            logger.error(f"Pain Point 검색 실패: {str(e)}")
            return []

    def search_similar_contents(
        self,
        query_text: str,
        n_results: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        유사한 원본 콘텐츠 검색

        Args:
            query_text: 검색할 텍스트
            n_results: 반환할 최대 결과 수
            min_similarity: 최소 유사도

        Returns:
            유사한 콘텐츠 목록
        """
        try:
            # Embedding 생성
            query_embedding = self.create_embedding(query_text)

            # 검색
            results = self.raw_contents_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # 결과 파싱
            similar_contents = []

            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance

                    if similarity < min_similarity:
                        continue

                    similar_content = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i][:200] + '...',
                        'similarity': round(similarity, 3),
                        'metadata': results['metadatas'][0][i]
                    }
                    similar_contents.append(similar_content)

            logger.info(f"유사 콘텐츠 {len(similar_contents)}개 발견")

            return similar_contents

        except Exception as e:
            logger.error(f"콘텐츠 검색 실패: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict:
        """컬렉션 통계 조회"""
        stats = {
            'pain_points_count': self.pain_points_collection.count(),
            'raw_contents_count': self.raw_contents_collection.count()
        }
        return stats


def test_rag_engine():
    """RAG 엔진 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("=" * 60)
    logger.info("RAG Engine 테스트")
    logger.info("=" * 60)

    try:
        rag = RAGEngine()

        # 통계 조회
        stats = rag.get_collection_stats()
        logger.info(f"\n현재 통계:")
        logger.info(f"  - Pain Points: {stats['pain_points_count']}개")
        logger.info(f"  - Raw Contents: {stats['raw_contents_count']}개")

        # 테스트 데이터 추가
        logger.info("\n" + "=" * 60)
        logger.info("테스트 데이터 추가")
        logger.info("=" * 60)

        # Pain Point 추가
        test_pain_points = [
            {
                'id': 1001,
                'problem_statement': '프리랜서들이 수동으로 청구서를 작성하는데 많은 시간을 낭비함',
                'problem_detail': '엑셀로 청구서를 만들고, 이메일로 보내고, 결제를 추적하는 과정이 반복적이고 시간 소모적임',
                'metadata': {
                    'affected_users': '프리랜서',
                    'severity': 'high',
                    'frequency': 'weekly'
                }
            },
            {
                'id': 1002,
                'problem_statement': '소규모 비즈니스 오너들이 회계 처리에 어려움을 겪음',
                'problem_detail': 'QuickBooks는 너무 복잡하고 비싸며, 수동 처리는 오류가 많음',
                'metadata': {
                    'affected_users': '소상공인',
                    'severity': 'high',
                    'frequency': 'monthly'
                }
            },
            {
                'id': 1003,
                'problem_statement': '개발자들이 API 문서 작성과 관리에 많은 시간을 소비함',
                'problem_detail': 'API가 변경될 때마다 문서를 수동으로 업데이트해야 하고, 팀원들과 동기화가 어려움',
                'metadata': {
                    'affected_users': '개발자',
                    'severity': 'medium',
                    'frequency': 'daily'
                }
            }
        ]

        for pp in test_pain_points:
            success = rag.add_pain_point(
                pp['id'],
                pp['problem_statement'],
                pp['problem_detail'],
                pp['metadata']
            )
            if success:
                logger.info(f"  ✓ Pain Point {pp['id']} 추가 완료")

        # 유사 검색 테스트
        logger.info("\n" + "=" * 60)
        logger.info("유사 Pain Point 검색 테스트")
        logger.info("=" * 60)

        query = "I spend too much time creating invoices for my consulting clients"
        logger.info(f"\n검색 쿼리: {query}")

        similar = rag.search_similar_pain_points(query, n_results=3, min_similarity=0.5)

        if similar:
            logger.info(f"\n유사한 Pain Point {len(similar)}개 발견:")
            for i, sp in enumerate(similar, 1):
                logger.info(f"\n[{i}] 유사도: {sp['similarity']}")
                logger.info(f"문제: {sp['problem_statement']}")
                logger.info(f"사용자: {sp['metadata'].get('affected_users', 'N/A')}")
                logger.info(f"심각도: {sp['metadata'].get('severity', 'N/A')}")
        else:
            logger.info("\n유사한 Pain Point를 찾지 못했습니다.")

        # 최종 통계
        logger.info("\n" + "=" * 60)
        stats = rag.get_collection_stats()
        logger.info(f"최종 통계:")
        logger.info(f"  - Pain Points: {stats['pain_points_count']}개")
        logger.info(f"  - Raw Contents: {stats['raw_contents_count']}개")
        logger.info("=" * 60)

    except ValueError as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        logger.error("\n.env 파일에 OPENAI_API_KEY를 추가하거나")
        logger.error("환경변수로 설정해주세요:")
        logger.error("  export OPENAI_API_KEY='your_api_key'")

    except Exception as e:
        logger.error(f"\n테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rag_engine()
