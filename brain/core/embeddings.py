from typing import List

class EmbeddingsService:
    def generate_embedding(self, text: str) -> List[float]:
        # Return a mock 768-dimensional vector (zeros)
        # In v2.0, this will call a real model
        return [0.0] * 768

embeddings_service = EmbeddingsService()
