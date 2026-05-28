from typing import Any

from pydantic import BaseModel, Field


# 검색 요청
class SearchRequest(BaseModel):
    # 질문
    query: str = Field(..., description="검색할 질문 또는 키워드")


# parent chunk 정보
class ParentSearchResult(BaseModel):
    # parent chunk id
    chunk_id: int

    # parent chunk index
    chunk_index: int

    # parent chunk 내용
    content: str

    # parent chunk metadata
    metadata: dict[str, Any] | None = None


# 검색 결과 단건
class SearchResult(BaseModel):
    # 유사도 점수
    score: float

    # child chunk id
    chunk_id: int

    # 문서 id
    document_id: int

    # 문서 제목
    document_title: str

    # parent chunk id
    parent_chunk_id: int | None = None

    # 문서 내 child chunk 순서
    chunk_index: int

    # child chunk 내용
    content: str

    # child chunk metadata
    metadata: dict[str, Any] | None = None

    # parent chunk 정보
    parent: ParentSearchResult | None = None


# 검색 응답
class SearchResponse(BaseModel):
    # 사용자 질문
    query: str

    # 검색 대상 문서 id
    # 전체 검색이면 None
    document_id: int | None = None

    # 검색 결과 수
    top_k: int

    # 검색 결과 목록
    results: list[SearchResult] = Field(default_factory=list)