from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class DocumentEmbeddingService:
    # 생성자
    def __init__(self):
        self.document_repository = DocumentRepository()
        self.chunk_repository = ChunkRepository()

        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    # 문서의 child chunk를 embedding 후 Qdrant에 저장
    def embed_document(
        self,
        db: Session,
        document_id: int,
    ) -> dict:
        try:
            document = self.document_repository.find_by_id(
                db=db,
                document_id=document_id,
            )

            if document is None:
                raise ValueError("문서를 찾을 수 없습니다.")

            if document.status not in ["parsed", "embedded"]:
                raise ValueError(
                    f"parsed 또는 embedded 상태의 문서만 embedding할 수 있습니다. current_status={document.status}"
                )

            child_chunks = self.chunk_repository.find_unembedded_child_chunks_by_document_id(
                db=db,
                document_id=document_id,
            )

            if not child_chunks:
                return {
                    "document_id": document.id,
                    "status": document.status,
                    "embedded_count": 0,
                    "message": "embedding할 child chunk가 없습니다.",
                }

            texts = [
                chunk.content
                for chunk in child_chunks
            ]

            embeddings = self.embedding_service.embed_texts(texts)

            if len(child_chunks) != len(embeddings):
                raise ValueError(
                    f"chunk 수와 embedding 수가 일치하지 않습니다. "
                    f"chunks={len(child_chunks)}, embeddings={len(embeddings)}"
                )

            for chunk, embedding in zip(child_chunks, embeddings):
                point_id = chunk.id

                payload = self.qdrant_service.build_chunk_payload(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    parent_chunk_id=chunk.parent_chunk_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    metadata=chunk.metadata_json,
                )

                self.qdrant_service.upsert_point(
                    point_id=point_id,
                    vector=embedding,
                    payload=payload,
                )

                self.chunk_repository.update_qdrant_point_id(
                    db=db,
                    chunk=chunk,
                    qdrant_point_id=str(point_id),
                )

            self.document_repository.update_status(
                db=db,
                document=document,
                status="embedded",
            )

            db.commit()
            db.refresh(document)

            return {
                "document_id": document.id,
                "status": document.status,
                "embedded_count": len(child_chunks),
                "message": "embedding이 완료되었습니다.",
            }

        except Exception:
            db.rollback()
            raise