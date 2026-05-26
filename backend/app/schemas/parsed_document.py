from pydantic import BaseModel, Field
from app.schemas.chunk import ParentChunk

# 파싱된 문서의 개별 요소
class ParsedElement(BaseModel):
    # element 유형
    # title, section_heading, paragraph, table, figure, image_placeholder, unknown
    element_type: str

    # element 내용
    text: str

    # 페이지 번호
    page_number: int | None = None

    # 추가 정보
    metadata: dict = Field(default_factory=dict)


# 파싱된 문서 전체 결과
class ParsedDocument(BaseModel):
    # 문서 id
    document_id: int

    # 사용한 parser
    parser: str

    # 파싱 결과
    elements: list[ParsedElement] = Field(default_factory=list)

    # parent chunk
    parent_chunks: list[ParentChunk] = Field(default_factory=list)

    # 문서 전체 글자 수
    total_char_count: int = 0

    # 원본 Markdown
    raw_markdown: str | None = None