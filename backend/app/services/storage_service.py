import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class StorageService:
    # 생성자
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)

    # 파일 저장
    def save_pdf(self, file: UploadFile) -> tuple[str, int]:
        
        # 파일명에서 확장자를 소문자로 추출
        extension = Path(file.filename or "").suffix.lower()

        # 확장자가 pdf가 아니라면 에러
        if extension != ".pdf":
            raise ValueError("PDF 파일만 업로드할 수 있습니다.")

        # 파일 식별키 생성
        storage_key = f"papers/{uuid4()}.pdf"

        # 저장 경로
        save_path = self.upload_dir / storage_key

        # 폴더 없으면 생성
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 내용을 복사하여 저장
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 파일 사이즈 계산
        file_size = save_path.stat().st_size

        return storage_key, file_size