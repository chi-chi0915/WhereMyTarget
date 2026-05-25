
from pathlib import Path

import fitz

from experiments.parser_compare.common import (
    build_header,
    build_output_path,
    get_sample_pdfs,
    write_text,
)

PARSER_NAME = "pymupdf_baseline"

# PDF를 PyMuPDF로 읽고 Markdown 문자열로 변환
def parse_pdf(pdf_path: Path) -> str:
    
    lines: list[str] = []

    # PyMuPDF으로 PDF를 열음
    with fitz.open(pdf_path) as pdf:
        
        for page_index, page in enumerate(pdf):
            # 현재 페이지에서 텍스트 추출
            text = page.get_text("text").strip()

            # 페이지 구분을 위한 제목 추가
            lines.append(f"\n\n## Page {page_index + 1}\n\n")

            lines.append(text)

    return "\n".join(lines).strip()


# PDF를 parser 이름으로 파싱
def run_parser(parser_name: str) -> None:

    pdfs = get_sample_pdfs()

    # PDF가 하나도 없으면 종료
    if not pdfs:
        print("[PyMuPDF] sample_pdfs 폴더에 PDF가 없습니다.")
        return

    # PDF 파일을 하나씩 파싱
    for pdf_path in pdfs:
        print(f"[PyMuPDF] parsing: {pdf_path.name}")

        try:
            content = build_header(PARSER_NAME, pdf_path)

            content += parse_pdf(pdf_path)

            output_path = build_output_path(PARSER_NAME, pdf_path, ".md")
            
            write_text(output_path, content)

            print(f"[PyMuPDF] saved: {output_path}")

        except Exception as e:
            # 파싱 중 에러가 나면 에러 파일로 저장
            output_path = build_output_path(PARSER_NAME, pdf_path, ".error.txt")
            write_text(output_path, repr(e))

            print(f"[PyMuPDF] failed: {pdf_path.name}")
            print(e)


# PDF를 PyMuPDF으로 파싱
def run() -> None:
    run_parser(PARSER_NAME)

# 이 파일을 직접 실행했을 때 run() 실행
if __name__ == "__main__":
    run()