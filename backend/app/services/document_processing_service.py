import os

from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.services.pdf_parser_service import PdfParserService
from app.services.storage_service import StorageService
from app.schemas.parsed_document import ParsedDocument


class DocumentProcessingService:
    # 생성자
    def __init__(self):
        # 환경 변수에서 저장 경로를 읽음
        upload_dir = os.getenv("LOCAL_UPLOAD_DIR")

        if upload_dir is None:
            raise ValueError("LOCAL_UPLOAD_DIR 환경변수가 설정되지 않았습니다.")

        # 객체 초기화
        self.document_repository = DocumentRepository()
        self.storage_service = StorageService(upload_dir)
        self.pdf_parser_service = PdfParserService()

    def parse_document(self, db: Session, document_id: int) -> ParsedDocument:
        document = self.document_repository.find_by_id(db, document_id)

        # 문서나 원본이 없다면 에러
        if document is None:
            raise ValueError("문서를 찾을 수 없습니다.")

        if document.file is None:
            raise ValueError("원본을 찾을 수 없습니다.")

        # key를 통해 파일 경로로 변환
        file_path = self.storage_service.get_file_path(document.file.storage_key)

        # 경로가 없다면 에러
        if not file_path.exists():
            raise ValueError("저장된 PDF 파일을 찾을 수 없습니다.")

        return self.pdf_parser_service.parse(
            document_id=document.id,
            file_path=file_path,
        )