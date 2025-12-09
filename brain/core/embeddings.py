from typing import List
from core.local_model_engine import local_engine

class EmbeddingsService:
    def generate_embedding(self, text: str) -> List[float]:
        return local_engine.embed(text)

embeddings_service = EmbeddingsService()
