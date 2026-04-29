import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService


class DocumentService:
    # 생성자
    def __init__(self):
        # 환경 변수에서 저장 경로를 읽음
        upload_dir = os.getenv("LOCAL_UPLOAD_DIR")

        if upload_dir is None:
            raise ValueError("LOCAL_UPLOAD_DIR 환경변수가 설정되지 않았습니다.")

        # 객체 초기화
        self.storage_service = StorageService(upload_dir)
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