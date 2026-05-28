from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings

# 벡터를 저장하고 검색
class QdrantService:
    # 생성자
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.embedding_vector_size

    # collection이 없으면 생성
    def ensure_collection(self) -> None:
        if self.client.collection_exists(
            collection_name=self.collection_name,
        ):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )

    # 단일 point 저장
    def upsert_point(
        self,
        point_id: int,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        self.ensure_collection()

        if len(vector) != self.vector_size:
            raise ValueError(
                f"embedding vector 크기가 일치하지 않습니다. "
                f"expected={self.vector_size}, actual={len(vector)}"
            )

        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload,
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

    # 복수 point 저장
    def upsert_points(
        self,
        points: list[PointStruct],
    ) -> None:
        self.ensure_collection()

        if not points:
            return

        for point in points:
            if point.vector is None:
                raise ValueError(f"point vector가 비어 있습니다. point_id={point.id}")

            if len(point.vector) != self.vector_size:
                raise ValueError(
                    f"embedding vector 크기가 일치하지 않습니다. "
                    f"point_id={point.id}, expected={self.vector_size}, actual={len(point.vector)}"
                )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    # child chunk payload 생성
    def build_chunk_payload(
        self,
        document_id: int,
        chunk_id: int,
        parent_chunk_id: int | None,
        chunk_index: int,
        content: str,
        metadata: dict | None,
    ) -> dict[str, Any]:
        payload = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "parent_chunk_id": parent_chunk_id,
            "chunk_index": chunk_index,
            "content": content,
        }

        if metadata:
            payload.update(metadata)

        return payload