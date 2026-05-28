from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class SearchService:
    # 생성자
    def __init__(self):
        self.chunk_repository = ChunkRepository()
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    # 문서 chunk 검색
    def search(
        self,
        db: Session,
        query: str,
        document_id: int | None = None,
    ) -> dict:
        if query is None or query.strip() == "":
            raise ValueError("검색어가 비어 있습니다.")

        search_top_k = settings.search_top_k
        score_threshold = settings.search_score_threshold

        query_vector = self.embedding_service.embed_text(query)

        qdrant_results = self.qdrant_service.search_points(
            query_vector=query_vector,
            top_k=search_top_k,
            document_id=document_id,
        )

        if not qdrant_results:
            return {
                "query": query,
                "document_id": document_id,
                "top_k": search_top_k,
                "results": [],
            }

        chunk_ids = [
            int(result.id)
            for result in qdrant_results
            if result.score >= score_threshold
        ]

        if not chunk_ids:
            return {
                "query": query,
                "document_id": document_id,
                "top_k": search_top_k,
                "results": [],
            }

        chunks = self.chunk_repository.find_by_ids(
            db=db,
            chunk_ids=chunk_ids,
        )

        # 매핑
        chunk_by_id = {
            chunk.id: chunk
            for chunk in chunks
        }

        results = []

        # Qdrant 순서대로 재조립
        for result in qdrant_results:
            if result.score < score_threshold:
                continue

            chunk_id = int(result.id)
            chunk = chunk_by_id.get(chunk_id)

            if chunk is None:
                continue

            parent = None

            if chunk.parent is not None:
                parent = {
                    "chunk_id": chunk.parent.id,
                    "chunk_index": chunk.parent.chunk_index,
                    "content": chunk.parent.content,
                    "metadata": chunk.parent.metadata_json,
                }

            results.append(
                {
                    "score": result.score,
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": chunk.document.title,
                    "parent_chunk_id": chunk.parent_chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata_json,
                    "parent": parent,
                }
            )

        return {
            "query": query,
            "document_id": document_id,
            "top_k": search_top_k,
            "results": results,
        }