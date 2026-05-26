from app.schemas.parsed_document import ParsedElement
from app.schemas.chunk import ParentChunk


class ChunkingService:
    # ParsedElement 목록을 parent chunk 목록으로 변환
    def create_parent_chunks(self, elements: list[ParsedElement]) -> list[ParentChunk]:
        parent_chunks: list[ParentChunk] = []

        current_section_title: str | None = None
        current_contents: list[str] = []
        current_element_types: list[str] = []

        for element in elements:
            # 현재 의미 없는 image placeholder 제외
            if element.element_type == "image_placeholder":
                continue

            # section_heading이 나오면 새 chunk 시작
            if element.element_type == "section_heading":
                if current_contents:
                    parent_chunks.append(
                        self._create_parent_chunk(
                            chunk_index=len(parent_chunks),
                            section_title=current_section_title,
                            contents=current_contents,
                            element_types=current_element_types,
                        )
                    )

                current_section_title = element.text
                current_contents = [element.text]
                current_element_types = [element.element_type]
                continue

            current_contents.append(element.text)
            current_element_types.append(element.element_type)

        # 마지막 chunk 저장
        if current_contents:
            parent_chunks.append(
                self._create_parent_chunk(
                    chunk_index=len(parent_chunks),
                    section_title=current_section_title,
                    contents=current_contents,
                    element_types=current_element_types,
                )
            )

        return parent_chunks

    # parent chunk 객체 생성
    def _create_parent_chunk(
        self,
        chunk_index: int,
        section_title: str | None,
        contents: list[str],
        element_types: list[str],
    ) -> ParentChunk:
        return ParentChunk(
            chunk_index=chunk_index,
            section_title=section_title,
            content="\n\n".join(contents).strip(),
            element_types=list(element_types),
            metadata={
                "element_count": len(contents),
            },
        )