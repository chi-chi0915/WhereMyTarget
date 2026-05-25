from pathlib import Path

from langchain_community.document_loaders import UnstructuredPDFLoader

from experiments.parser_compare.common import (
    build_header,
    build_output_path,
    get_sample_pdfs,
    write_text,
)


# PDF를 LangChain Document로 읽고 Markdown 문자열로 변환
def format_documents(docs) -> str:

    lines: list[str] = []

    for index, doc in enumerate(docs, start=1):
        # Metadata 저장
        metadata = doc.metadata or {}

        # Element 번호 표시
        lines.append(f"\n\n## Element {index}\n")

        # Metadata 영역 표시
        lines.append("### Metadata\n")
        lines.append("```text")

        # metadata의 key-value를 한 줄씩 기록
        for key, value in metadata.items():
            lines.append(f"{key}: {value}")

        lines.append("```")

        # 파싱된 텍스트 저장
        lines.append("\n### Content\n")
        lines.append(doc.page_content.strip())

    return "\n".join(lines).strip()


# PDF를 Unstructured로 파싱
def parse_pdf(pdf_path: Path, strategy: str) -> str:
    # mode="elements" PDF를 문서 요소 단위로 받음
    loader = UnstructuredPDFLoader(
        str(pdf_path),
        mode="single",
        strategy=strategy,
        chunking_strategy="by_title",
        max_characters=1500,
        combine_text_under_n_chars=300,
    )

    # PDF를 파싱해서 LangChain Document 리스트로 반환
    docs = loader.load()

    # Document 리스트를 Markdown 문자열로 변환
    return format_documents(docs)


# strategy으로 PDF를 파싱
def run_parser(strategy: str) -> None:
    
    parser_name = f"unstructured_{strategy}"
    pdfs = get_sample_pdfs()

    # PDF가 하나도 없으면 종료
    if not pdfs:
        print(f"[Unstructured:{strategy}] sample_pdfs 폴더에 PDF가 없습니다.")
        return

    # PDF를 하나씩 파싱
    for pdf_path in pdfs:
        print(f"[Unstructured:{strategy}] parsing: {pdf_path.name}")

        try:
            content = build_header(parser_name, pdf_path)
            
            content += parse_pdf(pdf_path, strategy)
            
            output_path = build_output_path(parser_name, pdf_path, ".md")

            write_text(output_path, content)

            print(f"[Unstructured:{strategy}] saved: {output_path}")

        except Exception as e:
            # 파싱 중 에러가 나면 에러 파일로 저장
            output_path = build_output_path(parser_name, pdf_path, ".error.txt")
            write_text(output_path, repr(e))

            print(f"[Unstructured:{strategy}] failed: {pdf_path.name}")
            print(e)


# PDF를 unstructured로 파싱
def run() -> None:
    # 빠른 파싱 전략
    run_parser("fast")

    # layout-aware 성격이 더 강한 고해상도 파싱 전략
    # run_parser("hi_res")


# 이 파일을 직접 실행했을 때 run() 실행
if __name__ == "__main__":
    run()