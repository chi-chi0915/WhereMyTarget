from pathlib import Path

from langchain_community.document_loaders import PDFPlumberLoader

from experiments.parser_compare.common import (
    build_header,
    build_output_path,
    get_sample_pdfs,
    write_text,
)


PARSER_NAME = "pdfplumber"


# LangChain Document 리스트를 Markdown 문자열로 변환
def format_documents(docs) -> str:
    lines: list[str] = []

    for index, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}

        lines.append(f"\n\n## Page Document {index}\n")

        # 비교에 필요한 metadata만 저장
        lines.append("### Metadata\n")
        lines.append("```text")
        lines.append(f"page: {metadata.get('page')}")
        lines.append(f"total_pages: {metadata.get('total_pages')}")
        lines.append(f"source: {metadata.get('source')}")
        lines.append("```")

        # PDFPlumber가 추출한 페이지 텍스트 저장
        lines.append("\n### Content\n")
        lines.append(doc.page_content.strip())

    return "\n".join(lines).strip()


# PDF 1개를 PDFPlumber로 읽고 Markdown 문자열로 변환
def parse_pdf(pdf_path: Path) -> str:
    # PDFPlumberLoader는 pdfplumber 기반 LangChain PDF loader
    loader = PDFPlumberLoader(str(pdf_path))

    # PDF를 LangChain Document 리스트로 로드
    docs = loader.load()

    # Document 리스트를 Markdown 문자열로 변환
    return format_documents(docs)


# PDFPlumber parser로 sample_pdfs의 모든 PDF를 실행
def run_parser(parser_name: str) -> None:
    pdfs = get_sample_pdfs()

    # PDF가 하나도 없으면 종료
    if not pdfs:
        print(f"[{parser_name}] sample_pdfs 폴더에 PDF가 없습니다.")
        return

    # PDF를 하나씩 파싱
    for pdf_path in pdfs:
        print(f"[{parser_name}] parsing: {pdf_path.name}")

        try:
            # 결과 파일 상단 헤더 생성
            content = build_header(parser_name, pdf_path)

            # PDFPlumber 파싱 결과를 헤더 뒤에 추가
            content += parse_pdf(pdf_path)

            # 저장할 결과 파일 경로 생성
            output_path = build_output_path(parser_name, pdf_path, ".md")

            # 결과 저장
            write_text(output_path, content)

            print(f"[{parser_name}] saved: {output_path}")

        except Exception as e:
            # 파싱 중 에러가 나면 에러 파일로 저장
            output_path = build_output_path(parser_name, pdf_path, ".error.txt")
            write_text(output_path, repr(e))

            print(f"[{parser_name}] failed: {pdf_path.name}")
            print(e)


# PDFPlumber parser 실행
def run() -> None:
    run_parser(PARSER_NAME)


# 이 파일을 직접 실행했을 때 run() 실행
if __name__ == "__main__":
    run()