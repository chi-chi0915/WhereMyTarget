from datetime import datetime

from pydantic import BaseModel, Field


# 문서 단건
class DocumentListItem(BaseModel):
    id: int
    title: str
    document_type: str
    status: str
    created_at: datetime
    updated_at: datetime


# 문서 파일 정보
class DocumentFileInfo(BaseModel):
    original_filename: str
    storage_key: str
    content_type: str | None = None
    file_size: int | None = None
    created_at: datetime


# 문서 chunk 통계
class DocumentChunkStats(BaseModel):
    total_count: int = 0
    parent_count: int = 0
    child_count: int = 0
    embedded_child_count: int = 0


# 문서 상세
class DocumentDetailResponse(BaseModel):
    id: int
    title: str
    document_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    file: DocumentFileInfo | None = None
    chunk_stats: DocumentChunkStats = Field(default_factory=DocumentChunkStats)