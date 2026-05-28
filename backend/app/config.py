import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

class Settings:
    # DB 설정
    database_url: str

    # 업로드 경로
    local_upload_dir: str

    # child chunk 제한
    child_chunk_target_size: int

    # 검색 결과 개수
    search_top_k: int

    # Qdrant 설정
    qdrant_url: str
    qdrant_collection_name: str

    # Embedding 설정
    embedding_provider: str
    embedding_model: str
    embedding_vector_size: int
    openai_api_key: str

    def __init__(self):
        self.database_url = self._get_required_env("DATABASE_URL")

        self.local_upload_dir = self._get_required_env("LOCAL_UPLOAD_DIR")
        
        self.child_chunk_target_size = self._get_int_env(
            key="CHILD_CHUNK_TARGET_SIZE",
            default_value=700,
        )

        self.search_top_k = self._get_int_env(
            key="SEARCH_TOP_K",
            default_value=5,
        )

        self.qdrant_url = self._get_required_env("QDRANT_URL")

        self.qdrant_collection_name = self._get_env(
            key="QDRANT_COLLECTION_NAME",
            default_value="paper_chunks",
        )

        self.embedding_provider = self._get_env(
            key="EMBEDDING_PROVIDER",
            default_value="openai",
        )

        self.embedding_model = self._get_env(
            key="EMBEDDING_MODEL",
            default_value="text-embedding-3-small",
        )

        self.embedding_vector_size = self._get_int_env(
            key="EMBEDDING_VECTOR_SIZE",
            default_value=1536,
        )

        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")

    # 환경변수 조회
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)

        if value is None or value.strip() == "":
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")

        return value

    def _get_env(self, key: str, default_value: str) -> str:
        value = os.getenv(key)

        if value is None or value.strip() == "":
            return default_value

        return value

    def _get_int_env(self, key: str, default_value: int) -> int:
        value = os.getenv(key)

        if value is None:
            return default_value

        try:
            return int(value)

        except ValueError:
            raise ValueError(f"{key} 환경변수는 숫자여야 합니다.")


settings = Settings()