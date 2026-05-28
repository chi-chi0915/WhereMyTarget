import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.services.storage_service import StorageService
from app.services.qdrant_service import QdrantService

from app.repositories.document_repository import DocumentRepository

from app.schemas.document import (
    DocumentChunkStats,
    DocumentDetailResponse,
    DocumentFileInfo,
    DocumentListItem,
)

class DocumentService:
    # 생성자
    def __init__(self):
        # 환경 변수에서 저장 경로를 읽음
        upload_dir = os.getenv("LOCAL_UPLOAD_DIR")

        if upload_dir is None:
            raise ValueError("LOCAL_UPLOAD_DIR 환경변수가 설정되지 않았습니다.")

        # 객체 초기화
        self.storage_service = StorageService(upload_dir)
        self.qdrant_service = QdrantService()
        self.document_repository = DocumentRepository()

    # 파일을 저장하고 트랜잭션으로 메타 데이터 DB에 저장
    def create_document(self, file: UploadFile, db: Session):
        try:
            storage_key, file_size = self.storage_service.save_pdf(file)

            title = file.filename or "untitled.pdf"

            document = self.document_repository.create_document(
                db=db,
                title=title,
                document_type="paper",
                status="uploaded",
            )

            document_file = self.document_repository.create_document_file(
                db=db,
                document_id=document.id,
                original_filename=title,
                storage_key=storage_key,
                content_type=file.content_type,
                file_size=file_size,
            )

            db.commit()
            db.refresh(document)
            db.refresh(document_file)

            return {
                "document_id": document.id,
                "title": document.title,
                "status": document.status,
                "original_filename": document_file.original_filename,
                "content_type": document_file.content_type,
                "file_size": document_file.file_size,
            }

        # 에러나면 롤백
        except Exception:
            db.rollback()
            raise
    
    # 문서 목록 조회
    def find_documents(self, db: Session) -> list[DocumentListItem]:
        documents = self.document_repository.find_all(db=db)

        return [
            DocumentListItem(
                id=document.id,
                title=document.title,
                document_type=document.document_type,
                status=document.status,
                created_at=document.created_at,
                updated_at=document.updated_at,
            )
            for document in documents
        ]

    # 문서 상세 조회
    def find_document_detail(
        self,
        db: Session,
        document_id: int,
    ) -> DocumentDetailResponse:
        document = self.document_repository.find_detail_by_id(
            db=db,
            document_id=document_id,
        )

        if document is None:
            raise ValueError("문서를 찾을 수 없습니다.")

        total_count = len(document.chunks)
        parent_count = sum(
            1 for chunk in document.chunks
            if chunk.chunk_type == "parent"
        )
        child_count = sum(
            1 for chunk in document.chunks
            if chunk.chunk_type == "child"
        )
        embedded_child_count = sum(
            1 for chunk in document.chunks
            if chunk.chunk_type == "child" and chunk.qdrant_point_id is not None
        )

        file_info = None

        if document.file is not None:
            file_info = DocumentFileInfo(
                original_filename=document.file.original_filename,
                storage_key=document.file.storage_key,
                content_type=document.file.content_type,
                file_size=document.file.file_size,
                created_at=document.file.created_at,
            )

        return DocumentDetailResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            file=file_info,
            chunk_stats=DocumentChunkStats(
                total_count=total_count,
                parent_count=parent_count,
                child_count=child_count,
                embedded_child_count=embedded_child_count,
            ),
        )
    
    # 문서 원본 파일 조회
    def get_document_file(
        self,
        db: Session,
        document_id: int,
    ):
        document = self.document_repository.find_detail_by_id(
            db=db,
            document_id=document_id,
        )

        if document is None:
            raise ValueError("문서를 찾을 수 없습니다.")

        if document.file is None:
            raise ValueError("문서 원본 파일을 찾을 수 없습니다.")

        file_path = self.storage_service.get_file_path(
            document.file.storage_key
        )

        if not file_path.exists():
            raise ValueError("저장된 원본 파일을 찾을 수 없습니다.")

        return file_path, document.file.original_filename
    
    # 문서 삭제
    def delete_document(
        self,
        db: Session,
        document_id: int,
    ) -> dict:
        try:
            document = self.document_repository.find_detail_by_id(
                db=db,
                document_id=document_id,
            )

            if document is None:
                raise ValueError("문서를 찾을 수 없습니다.")

            point_ids = [
                int(chunk.qdrant_point_id)
                for chunk in document.chunks
                if chunk.chunk_type == "child"
                and chunk.qdrant_point_id is not None
            ]

            self.qdrant_service.delete_points(
                point_ids=point_ids,
            )

            if document.file is not None:
                self.storage_service.delete_file(
                    storage_key=document.file.storage_key,
                )

            deleted_document_id = document.id
            deleted_title = document.title

            self.document_repository.delete_document(
                db=db,
                document=document,
            )

            db.commit()

            return {
                "document_id": deleted_document_id,
                "title": deleted_title,
                "deleted_qdrant_point_count": len(point_ids),
                "message": "문서가 삭제되었습니다.",
            }

        except Exception:
            db.rollback()
            raise