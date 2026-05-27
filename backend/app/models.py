from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BigInteger, UniqueConstraint, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


# 테이블 모델들의 공통 부모
Base = declarative_base()


# 문서
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    # 문서 제목
    title = Column(String(500), nullable=False)

    # 문서 유형 (PDF, youtube)
    document_type = Column(String(50), nullable=False, default="paper")

    # 문서 처리 상태
    status = Column(String(50), nullable=False, default="uploaded")

    # 생성 날짜
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 변경 날짜
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ORM 관계
    # back_populates는 반대편 relationship 속성과 연결
    # cascade는 부모 객체 삭제 시 자식 객체도 함께 삭제되도록 하는 설정
    file = relationship("DocumentFile", back_populates="document", uselist=False, cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


# 원본 문서 정보
class DocumentFile(Base):
    __tablename__ = "document_files"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)

    # 원본 문서명
    original_filename = Column(String(500), nullable=False)

    # 실제 저장 키
    storage_key = Column(String(1000), nullable=False, unique=True)

    # 문서 타입 (pdf, txt)
    content_type = Column(String(100), nullable=True)

    # 문서 크기(byte)
    file_size = Column(BigInteger, nullable=True)

    # 생성 날짜
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ORM 관계
    document = relationship("Document", back_populates="file")


# 문서에서 추출된 문단
class Chunk(Base):
    __tablename__ = "chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_type",
            "chunk_index",
            name="uq_chunks_document_type_index",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    # 문서 id
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    # 부모 chunk id
    parent_chunk_id = Column(Integer, ForeignKey("chunks.id", ondelete="CASCADE"), nullable=True)

    # chunk 타입(parent or child)
    chunk_type = Column(String(50), nullable=False)

    # 문서 내 chunk 번호
    chunk_index = Column(Integer, nullable=False)

    # chunk 내용
    content = Column(Text, nullable=False)

    # chunk 페이지
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)

    # 텍스트 수
    char_count = Column(Integer, nullable=True)

    # chunk 추가 정보
    metadata_json = Column("metadata", JSON, nullable=True)

    # Qdrant에 저장된 point id
    qdrant_point_id = Column(String(100), nullable=True)
    
    # 생성 날짜
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="chunks")

    parent = relationship(
        "Chunk",
        remote_side=[id],
        back_populates="children"
    )

    children = relationship(
        "Chunk",
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True
    )