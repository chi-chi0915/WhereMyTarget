from sqlalchemy.orm import Session, joinedload

from app.models import Document, DocumentFile


class DocumentRepository:
    # 파일 정보 저장
    def create_document(
        self,
        db: Session,
        title: str,
        document_type: str = "paper",
        status: str = "uploaded",
    ) -> Document:
        document = Document(
            title=title,
            document_type=document_type,
            status=status,
        )

        db.add(document)
        db.flush()

        return document

    # 원본 파일 정보 저장
    def create_document_file(
        self,
        db: Session,
        document_id: int,
        original_filename: str,
        storage_key: str,
        content_type: str | None,
        file_size: int | None,
    ) -> DocumentFile:
        document_file = DocumentFile(
            document_id=document_id,
            original_filename=original_filename,
            storage_key=storage_key,
            content_type=content_type,
            file_size=file_size,
        )

        db.add(document_file)
        db.flush()

        return document_file
    
    # 파일 단건 조회
    def find_by_id(
        self,
        db: Session,
        document_id: int,
    ) -> Document | None:
        return db.get(Document, document_id)

    # 문서 상태 변경
    def update_status(
        self,
        db: Session,
        document: Document,
        status: str,
    ) -> Document:
        document.status = status

        db.add(document)
        db.flush()

        return document
    
    # 문서 목록 조회
    def find_all(
        self,
        db: Session,
    ) -> list[Document]:
        return (
            db.query(Document)
            .order_by(Document.id.desc())
            .all()
        )

    # 문서 상세 조회
    def find_detail_by_id(
        self,
        db: Session,
        document_id: int,
    ) -> Document | None:
        return (
            db.query(Document)
            .options(
                joinedload(Document.file),
                joinedload(Document.chunks),
            )
            .filter(Document.id == document_id)
            .first()
        )
    
    # 문서 삭제
    def delete_document(
        self,
        db: Session,
        document: Document,
    ) -> None:
        db.delete(document)
        db.flush()