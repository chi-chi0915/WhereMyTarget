import re

from pathlib import Path
from docling.document_converter import DocumentConverter
from app.schemas.parsed_document import ParsedDocument, ParsedElement


class PdfParserService:
    # 생성자
    def __init__(self):        
        self.converter = DocumentConverter()
        
    # PDF를 Docling으로 파싱
    def parse(self, document_id: int, file_path: Path) -> ParsedDocument:
        
        # PDF를 Docling으로 읽고 Markdown으로 변환
        result = self.converter.convert(str(file_path))
        markdown = result.document.export_to_markdown()

        # Markdown을 내부 ParsedElement 구조로 변환
        elements = self._parse_markdown_to_elements(markdown)
        
        # 파싱 결과 반환
        return ParsedDocument(
            document_id=document_id,
            parser="docling",
            elements=elements,
            total_char_count=sum(len(element.text) for element in elements),
            raw_markdown=markdown,
        )

    # Markdown 문자열을 ParsedElement 리스트로 변환
    def _parse_markdown_to_elements(self, markdown: str) -> list[ParsedElement]:
        elements: list[ParsedElement] = []

        # 빈 줄 기준으로 Markdown block 분리
        blocks = re.split(r"\n\s*\n", markdown)

        for block in blocks:
            text = block.strip()

            # 빈 block이면 다음으로
            if not text:
                continue
        
            element = self._create_parsed_element(text)
            elements.append(element)

        return elements

    # ParsedElement로 변환
    def _create_parsed_element(self, text: str) -> ParsedElement:
        element_type = self._detect_element_type(text)
        metadata = {}

        # Markdown heading이면 ## 제거 후 heading_level 저장
        if text.startswith("#"):
            heading_level = self._get_heading_level(text)
            text = self._clean_heading_text(text)

            metadata["heading_level"] = heading_level

        return ParsedElement(
            element_type=element_type,
            text=text,
            page_number=None,
            metadata=metadata,
        )

    # element 유형 판단
    def _detect_element_type(self, text: str) -> str:
        # 이미지 placeholder
        if text == "<!-- image -->":
            return "image_placeholder"

        # Markdown table
        if self._is_markdown_table(text):
            return "table"

        # Markdown heading
        if text.startswith("#"):
            heading_text = text.lstrip("#").strip()

            if self._is_section_heading(heading_text):
                return "section_heading"

            return "title"

        # Table caption
        if self._is_table_caption(text):
            return "table_caption"

        # Figure subcaption
        if self._is_figure_subcaption(text):
            return "figure_subcaption"

        # Figure caption
        if self._is_figure_caption(text):
            return "figure"

        return "paragraph"

    # Markdown heading level 추출
    def _get_heading_level(self, text: str) -> int:
        match = re.match(r"^(#+)", text)

        if match is None:
            return 0

        return len(match.group(1)) 

    # Markdown heading에서 # 제거
    def _clean_heading_text(self, text: str) -> str:
        return text.lstrip("#").strip()

    # Markdown table 판단
    def _is_markdown_table(self, text: str) -> bool:
        lines = text.splitlines()

        if len(lines) < 2:
            return False

        # Markdown table은 | 로 시작하는 줄이 여러 개 있음
        table_line_count = sum(
            1 for line in lines
            if line.strip().startswith("|")
        )

        return table_line_count >= 2

    # table caption 판단
    def _is_table_caption(self, text: str) -> bool:
        return (
            re.match(r"^Table\s+\d+\.?", text) is not None
            or re.match(r"^표\s*\d+\.?", text) is not None
        )

    # 섹션 제목 판단
    def _is_section_heading(self, text: str) -> bool:
        # 로마자
        roman_section_pattern = r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\."

        # 숫자
        number_section_pattern = r"^\d+(\.\d+)*\s+"

        # 주요 섹션 제목
        named_section_headings = {
            "ACKNOWLEDGMENTS",
            "ACKNOWLEDGEMENTS",
            "REFERENCES",
            "ABSTRACT",
            "KEYWORDS",
        }

        return (
            re.match(roman_section_pattern, text) is not None
            or re.match(number_section_pattern, text) is not None
            or text.upper() in named_section_headings
        )

    # figure caption 판단
    def _is_figure_caption(self, text: str) -> bool:
        return (
            text.startswith("Fig.")
            or text.startswith("Figure")
            or text.startswith("그림")
        )
    
    # figure sub-caption 판단
    def _is_figure_subcaption(self, text: str) -> bool:
        return re.match(r"^\([a-zA-Z가-힣0-9]+\)\s+", text) is not None