from pathlib import Path
from datetime import datetime

# 폴더 경로
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_pdfs"
OUTPUT_DIR = BASE_DIR / "outputs"

# 확장자가 .pdf인 파일 가져옴
def get_sample_pdfs() -> list[Path]:
    return sorted(SAMPLE_DIR.glob("*.pdf"))

# 출력 폴더 생성
def ensure_output_dir(parser_name: str) -> Path:
    output_dir = OUTPUT_DIR / parser_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

# 결과 파일 경로 생성
def build_output_path(parser_name: str, pdf_path: Path, suffix: str = ".md") -> Path:
    output_dir = ensure_output_dir(parser_name)

    safe_stem = pdf_path.stem.replace(" ", "_")
    return output_dir / f"{safe_stem}{suffix}"

# 파일 저장
def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# 헤더 생성
def build_header(parser_name: str, pdf_path: Path) -> str:
    return (
        "# Parser Result\n\n"
        f"- parser: {parser_name}\n"
        f"- file: {pdf_path.name}\n"
        f"- created_at: {datetime.now().isoformat(timespec='seconds')}\n\n"
        "---\n\n"
    )