from pydantic import BaseModel, Field


# 사용자에게 보여줄 chunk
class ParentChunk(BaseModel):
    # chunk 유형
    chunk_type: str = "parent"

    # parent chunk 순서
    chunk_index: int

    # 섹션 제목
    section_title: str | None = None

    # parent chunk 내용
    content: str

    # chunk에 포함된 element type 목록
    element_types: list[str] = Field(default_factory=list)

    # 추가 정보
    metadata: dict = Field(default_factory=dict)


# embedding 검색에 사용할 chunk
class ChildChunk(BaseModel):
    # chunk 유형
    chunk_type: str = "child"

    # child chunk 순서
    chunk_index: int

    # parent chunk
    parent_chunk_index: int

    # child chunk 내용
    content: str

    # 추가 정보
    metadata: dict = Field(default_factory=dict)


# chunking 결과 전체
class ChunkingResult(BaseModel):
    # 문서 id
    document_id: int

    # parent chunk 목록
    parent_chunks: list[ParentChunk] = Field(default_factory=list)

    # child chunk 목록
    child_chunks: list[ChildChunk] = Field(default_factory=list)