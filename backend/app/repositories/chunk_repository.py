from sqlalchemy.orm import Session

from app.models import Chunk
from app.schemas.chunk import ParentChunk, ChildChunk


class ChunkRepository:
    # 단건 문서의 chunk 전체 삭제
    def delete_by_document_id(
        self,
        db: Session,
        document_id: int,
    ) -> None:
        db.query(Chunk).filter(
            Chunk.document_id == document_id
        ).delete(synchronize_session=False)

        db.flush()

    # parent chunk 저장
    def create_parent_chunk(
        self,
        db: Session,
        document_id: int,
        parent_chunk: ParentChunk,
    ) -> Chunk:
        chunk = Chunk(
            document_id=document_id,
            parent_chunk_id=None,
            chunk_type=parent_chunk.chunk_type,
            chunk_index=parent_chunk.chunk_index,
            content=parent_chunk.content,
            start_page=None,
            end_page=None,
            char_count=len(parent_chunk.content),
            metadata_json={
                "section_title": parent_chunk.section_title,
                "element_types": parent_chunk.element_types,
                **parent_chunk.metadata,
            },
        )

        db.add(chunk)
        db.flush()

        return chunk

    # child chunk 저장
    def create_child_chunk(
        self,
        db: Session,
        document_id: int,
        parent_chunk_id: int,
        child_chunk: ChildChunk,
    ) -> Chunk:
        chunk = Chunk(
            document_id=document_id,
            parent_chunk_id=parent_chunk_id,
            chunk_type=child_chunk.chunk_type,
            chunk_index=child_chunk.chunk_index,
            content=child_chunk.content,
            start_page=None,
            end_page=None,
            char_count=len(child_chunk.content),
            metadata_json=child_chunk.metadata,
        )

        db.add(chunk)
        db.flush()

        return chunk

    # chunk 저장
    def save_chunks(
        self,
        db: Session,
        document_id: int,
        parent_chunks: list[ParentChunk],
        child_chunks: list[ChildChunk],
    ) -> None:
        self.delete_by_document_id(
            db=db,
            document_id=document_id,
        )

        parent_index_to_db_id: dict[int, int] = {}

        for parent_chunk in parent_chunks:
            saved_parent_chunk = self.create_parent_chunk(
                db=db,
                document_id=document_id,
                parent_chunk=parent_chunk,
            )

            parent_index_to_db_id[parent_chunk.chunk_index] = saved_parent_chunk.id

        for child_chunk in child_chunks:
            parent_chunk_id = parent_index_to_db_id.get(child_chunk.parent_chunk_index)

            if parent_chunk_id is None:
                raise ValueError(
                    f"parent chunk을 찾을 수 없습니다. parent_chunk_index={child_chunk.parent_chunk_index}"
                )

            self.create_child_chunk(
                db=db,
                document_id=document_id,
                parent_chunk_id=parent_chunk_id,
                child_chunk=child_chunk,
            )

    
    # 단건 문서의 child chunk 조회
    def find_child_chunks_by_document_id(
        self,
        db: Session,
        document_id: int,
    ) -> list[Chunk]:
        return (
            db.query(Chunk)
            .filter(
                Chunk.document_id == document_id,
                Chunk.chunk_type == "child",
            )
            .order_by(Chunk.chunk_index.asc())
            .all()
        )

    # 단건 문서의 embedding 되지 않은 child chunk 조회
    def find_unembedded_child_chunks_by_document_id(
        self,
        db: Session,
        document_id: int,
    ) -> list[Chunk]:
        return (
            db.query(Chunk)
            .filter(
                Chunk.document_id == document_id,
                Chunk.chunk_type == "child",
                Chunk.qdrant_point_id.is_(None),
            )
            .order_by(Chunk.chunk_index.asc())
            .all()
        )

    # Qdrant point id 추가
    def update_qdrant_point_id(
        self,
        db: Session,
        chunk: Chunk,
        qdrant_point_id: str,
    ) -> Chunk:
        chunk.qdrant_point_id = qdrant_point_id

        db.add(chunk)
        db.flush()

        return chunk