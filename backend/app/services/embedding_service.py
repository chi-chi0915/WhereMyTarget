from openai import OpenAI

from app.config import settings

# 텍스트를 벡터로 전환
class EmbeddingService:
    # 생성자
    def __init__(self):
        if settings.embedding_provider != "openai":
            raise ValueError(
                f"지원하지 않는 embedding provider입니다. provider={settings.embedding_provider}"
            )

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    # 단일 텍스트 embedding 생성
    def embed_text(self, text: str) -> list[float]:
        if text is None or text.strip() == "":
            raise ValueError("embedding할 text가 비어 있습니다.")

        response = self.client.embeddings.create(
            model=self.model,
            input=text.strip(),
        )

        return response.data[0].embedding

    # 복수 텍스트 embedding 생성
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        for index, text in enumerate(texts):
            if text is None or text.strip() == "":
                raise ValueError(
                    f"embedding할 text 목록에 빈 값이 포함되어 있습니다. index={index}"
                )

        cleaned_texts = [
            text.strip()
            for text in texts
        ]

        response = self.client.embeddings.create(
            model=self.model,
            input=cleaned_texts,
        )

        return [
            item.embedding
            for item in response.data
        ]