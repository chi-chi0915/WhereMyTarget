from pathlib import Path

from docling.document_converter import DocumentConverter

from experiments.parser_compare.common import (
    build_header,
    build_output_path,
    get_sample_pdfs,
    write_text,
)


PARSER_NAME = "docling"


# PDF 1개를 Docling으로 읽고 Markdown 문자열로 변환
def parse_pdf(pdf_path: Path) -> str:
    # Docling의 문서 변환기 생성
    converter = DocumentConverter()

    # PDF 파일을 DoclingDocument 형태로 변환
    result = converter.convert(str(pdf_path))

    # 변환된 문서를 Markdown 문자열로 export
    return result.document.export_to_markdown()


# Docling으로 PDF를 파싱
def run_parser(parser_name: str) -> None:
    # sample_pdfs 폴더에서 PDF 목록 가져오기
    pdfs = get_sample_pdfs()

    # PDF가 하나도 없으면 종료
    if not pdfs:
        print(f"[{parser_name}] sample_pdfs 폴더에 PDF가 없습니다.")
        return

    # PDF를 하나씩 파싱
    for pdf_path in pdfs:
        print(f"[{parser_name}] parsing: {pdf_path.name}")

        try:
            content = build_header(parser_name, pdf_path)

            content += parse_pdf(pdf_path)

            output_path = build_output_path(parser_name, pdf_path, ".md")

            write_text(output_path, content)

            print(f"[{parser_name}] saved: {output_path}")

        except Exception as e:
            # 파싱 중 에러가 나면 에러 파일로 저장
            output_path = build_output_path(parser_name, pdf_path, ".error.txt")
            write_text(output_path, repr(e))

            print(f"[{parser_name}] failed: {pdf_path.name}")
            print(e)


# Docling parser 실행
def run() -> None:
    run_parser(PARSER_NAME)


# 이 파일을 직접 실행했을 때 run() 실행
if __name__ == "__main__":
    run()