import re

from app.schemas.parsed_document import ParsedElement
from app.schemas.chunk import ParentChunk, ChildChunk, ChunkingResult
from app.config import settings


class ChunkingService:
    # 생성자
    def __init__(self):
        self.child_chunk_target_size = settings.child_chunk_target_size

    # ParsedElement 목록을 parent/child chunk 목록으로 변환
    def create_chunks(
        self,
        document_id: int,
        elements: list[ParsedElement],
    ) -> ChunkingResult:
        parent_chunks: list[ParentChunk] = []
        child_chunks: list[ChildChunk] = []

        current_section_title: str | None = None
        current_elements: list[ParsedElement] = []

        for element in elements:
            # 의미 없는 부분 제외
            if element.element_type == "image_placeholder":
                continue

            # section_heading이 나오면 새 parent 시작
            if element.element_type == "section_heading":
                if current_elements:
                    parent_chunk = self._create_parent_chunk(
                        chunk_index=len(parent_chunks),
                        section_title=current_section_title,
                        elements=current_elements,
                    )

                    parent_chunks.append(parent_chunk)

                    child_chunks.extend(
                        self._create_child_chunks_from_elements(
                            parent_chunk=parent_chunk,
                            elements=current_elements,
                            start_chunk_index=len(child_chunks),
                        )
                    )

                current_section_title = element.text
                current_elements = [element]
                continue

            current_elements.append(element)

        # 마지막 parent chunk 저장
        if current_elements:
            parent_chunk = self._create_parent_chunk(
                chunk_index=len(parent_chunks),
                section_title=current_section_title,
                elements=current_elements,
            )

            parent_chunks.append(parent_chunk)

            child_chunks.extend(
                self._create_child_chunks_from_elements(
                    parent_chunk=parent_chunk,
                    elements=current_elements,
                    start_chunk_index=len(child_chunks),
                )
            )

        return ChunkingResult(
            document_id=document_id,
            parent_chunks=parent_chunks,
            child_chunks=child_chunks,
        )

    # parent chunk 객체 생성
    def _create_parent_chunk(
        self,
        chunk_index: int,
        section_title: str | None,
        elements: list[ParsedElement],
    ) -> ParentChunk:
        contents = [
            element.text
            for element in elements
            if element.element_type != "image_placeholder"
        ]

        element_types = [
            element.element_type
            for element in elements
            if element.element_type != "image_placeholder"
        ]

        return ParentChunk(
            chunk_index=chunk_index,
            section_title=section_title,
            content="\n\n".join(contents).strip(),
            element_types=list(element_types),
            metadata={
                "element_count": len(contents),
            },
        )

    # parent에 포함된 element 흐름을 기준으로 child chunk 생성
    def _create_child_chunks_from_elements(
        self,
        parent_chunk: ParentChunk,
        elements: list[ParsedElement],
        start_chunk_index: int,
    ) -> list[ChildChunk]:
        
        # 소개 파트는 한번에 처리
        if parent_chunk.section_title is None:
            searchable_elements = [
                element
                for element in elements
                if element.element_type != "image_placeholder"
            ]

            if not searchable_elements:
                return []

            return [
                self._create_child_chunk(
                    chunk_index=start_chunk_index,
                    parent_chunk_index=parent_chunk.chunk_index,
                    section_title=parent_chunk.section_title,
                    elements=searchable_elements,
                )
            ]
        
        child_chunks: list[ChildChunk] = []
        index = 0

        while index < len(elements):
            element = elements[index]

            # section_heading은 단독 child로 만들지 않고 metadata로만 활용
            if element.element_type == "section_heading":
                index += 1
                continue

            # image_placeholder는 검색용 child에서 제외
            if element.element_type == "image_placeholder":
                index += 1
                continue

            # table_caption 바로 다음이 table이면 함께 묶음
            if element.element_type == "table_caption":
                grouped_elements = [element]

                if self._has_next_element(elements, index, "table"):
                    grouped_elements.append(elements[index + 1])
                    index += 1

                child_chunks.append(
                    self._create_child_chunk(
                        chunk_index=start_chunk_index + len(child_chunks),
                        parent_chunk_index=parent_chunk.chunk_index,
                        section_title=parent_chunk.section_title,
                        elements=grouped_elements,
                    )
                )

                index += 1
                continue

            # table 단독 등장 시 child 생성
            if element.element_type == "table":
                child_chunks.append(
                    self._create_child_chunk(
                        chunk_index=start_chunk_index + len(child_chunks),
                        parent_chunk_index=parent_chunk.chunk_index,
                        section_title=parent_chunk.section_title,
                        elements=[element],
                    )
                )

                index += 1
                continue

            # figure_subcaption 바로 다음이 figure이면 함께 묶음
            if element.element_type == "figure_subcaption":
                grouped_elements = [element]

                if self._has_next_element(elements, index, "figure"):
                    grouped_elements.append(elements[index + 1])
                    index += 1

                child_chunks.append(
                    self._create_child_chunk(
                        chunk_index=start_chunk_index + len(child_chunks),
                        parent_chunk_index=parent_chunk.chunk_index,
                        section_title=parent_chunk.section_title,
                        elements=grouped_elements,
                    )
                )

                index += 1
                continue

            # figure 단독 등장 시 child 생성
            if element.element_type == "figure":
                child_chunks.append(
                    self._create_child_chunk(
                        chunk_index=start_chunk_index + len(child_chunks),
                        parent_chunk_index=parent_chunk.chunk_index,
                        section_title=parent_chunk.section_title,
                        elements=[element],
                    )
                )

                index += 1
                continue

            # paragraph는 길면 분할, 짧으면 그대로 child 생성
            if element.element_type == "paragraph":
                paragraph_children = self._create_paragraph_child_chunks(
                    element=element,
                    parent_chunk=parent_chunk,
                    start_chunk_index=start_chunk_index + len(child_chunks),
                )

                child_chunks.extend(paragraph_children)

                index += 1
                continue

            # 그 외 타입은 단독 child로 보존
            child_chunks.append(
                self._create_child_chunk(
                    chunk_index=start_chunk_index + len(child_chunks),
                    parent_chunk_index=parent_chunk.chunk_index,
                    section_title=parent_chunk.section_title,
                    elements=[element],
                )
            )

            index += 1

        return child_chunks

    # paragraph element를 child chunk로 변환
    def _create_paragraph_child_chunks(
        self,
        element: ParsedElement,
        parent_chunk: ParentChunk,
        start_chunk_index: int,
    ) -> list[ChildChunk]:
        target_size = self.child_chunk_target_size

        # 짧은 문단은 그대로 사용
        if len(element.text) <= target_size:
            return [
                self._create_child_chunk(
                    chunk_index=start_chunk_index,
                    parent_chunk_index=parent_chunk.chunk_index,
                    section_title=parent_chunk.section_title,
                    elements=[element],
                )
            ]

        # 긴 문단은 문장 단위로 분할
        sentences = self._split_sentences(element.text)

        child_chunks: list[ChildChunk] = []
        current_sentences: list[str] = []
        current_length = 0

        for sentence in sentences:
            if current_sentences and current_length + len(sentence) > target_size:
                content = " ".join(current_sentences).strip()

                child_chunks.append(
                    self._create_text_child_chunk(
                        chunk_index=start_chunk_index + len(child_chunks),
                        parent_chunk_index=parent_chunk.chunk_index,
                        section_title=parent_chunk.section_title,
                        content=content,
                        element_type="paragraph",
                    )
                )

                current_sentences = []
                current_length = 0

            current_sentences.append(sentence)
            current_length += len(sentence)

        # 마지막 문장 묶음 저장
        if current_sentences:
            content = " ".join(current_sentences).strip()

            child_chunks.append(
                self._create_text_child_chunk(
                    chunk_index=start_chunk_index + len(child_chunks),
                    parent_chunk_index=parent_chunk.chunk_index,
                    section_title=parent_chunk.section_title,
                    content=content,
                    element_type="paragraph",
                )
            )

        return child_chunks

    # child chunk 객체 생성
    def _create_child_chunk(
        self,
        chunk_index: int,
        parent_chunk_index: int,
        section_title: str | None,
        elements: list[ParsedElement],
    ) -> ChildChunk:
        content = "\n\n".join(element.text for element in elements).strip()
        element_types = [element.element_type for element in elements]

        return ChildChunk(
            chunk_index=chunk_index,
            parent_chunk_index=parent_chunk_index,
            content=content,
            metadata={
                "section_title": section_title,
                "element_types": element_types,
                "element_count": len(elements),
            },
        )

    # 문자열 content 기반 child chunk 생성
    def _create_text_child_chunk(
        self,
        chunk_index: int,
        parent_chunk_index: int,
        section_title: str | None,
        content: str,
        element_type: str,
    ) -> ChildChunk:
        return ChildChunk(
            chunk_index=chunk_index,
            parent_chunk_index=parent_chunk_index,
            content=content,
            metadata={
                "section_title": section_title,
                "element_types": [element_type],
                "element_count": 1,
            },
        )

    # 다음 element가 특정 type인지 확인
    def _has_next_element(
        self,
        elements: list[ParsedElement],
        current_index: int,
        expected_type: str,
    ) -> bool:
        next_index = current_index + 1

        if next_index >= len(elements):
            return False

        return elements[next_index].element_type == expected_type

    # 문장 단위로 분리
    def _split_sentences(self, text: str) -> list[str]:
        normalized_text = " ".join(text.split())

        sentences = re.split(r"(?<=[.!?。！？다])\s+", normalized_text)

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]