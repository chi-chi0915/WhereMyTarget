# 모든 parser 비교 실험을 한 번에 실행
def main() -> None:
    print("====== Parser Compare Start ======", flush=True)

    print("[run_all] PyMuPDF 시작", flush=True)
    from experiments.parser_compare import run_pymupdf
    run_pymupdf.run()

    print("[run_all] Unstructured 시작", flush=True)
    from experiments.parser_compare import run_unstructured
    run_unstructured.run()

    print("[run_all] Docling 시작", flush=True)
    from experiments.parser_compare import run_docling
    run_docling.run()

    print("[run_all] PyMuPDF4LLM 시작", flush=True)
    from experiments.parser_compare import run_pymupdf4llm
    run_pymupdf4llm.run()
    
    print("[run_all] PDFPlumber 시작", flush=True)
    from experiments.parser_compare import run_pdfplumber
    run_pdfplumber.run()

    print("====== Parser Compare Finished ======", flush=True)


# 이 파일을 직접 실행했을 때 main() 실행
if __name__ == "__main__":
    main()