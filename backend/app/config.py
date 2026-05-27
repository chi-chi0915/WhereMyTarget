import os


class Settings:
    # 업로드 경로
    local_upload_dir: str

    # child chunk 제한
    child_chunk_target_size: int

    def __init__(self):
        self.local_upload_dir = self._get_required_env("LOCAL_UPLOAD_DIR")
        self.child_chunk_target_size = self._get_int_env(
            key="CHILD_CHUNK_TARGET_SIZE",
            default_value=700,
        )

    # 환경변수 조회
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)

        if value is None:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")

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