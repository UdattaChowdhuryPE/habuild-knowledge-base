import os
import voyageai
from typing import List


class EmbeddingsService:
    def __init__(self):
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise ValueError("VOYAGE_API_KEY environment variable not set")
        self.client = voyageai.Client(api_key=api_key)

    def embed_document(self, text: str) -> List[float]:
        """Embed a document chunk for storage."""
        try:
            result = self.client.embed([text], model="voyage-3-lite", input_type="document")
            return result.embeddings[0]
        except Exception as e:
            print(f"Error embedding document: {e}")
            return []

    def embed_query(self, text: str) -> List[float]:
        """Embed a query for semantic search."""
        try:
            result = self.client.embed([text], model="voyage-3-lite", input_type="query")
            return result.embeddings[0]
        except Exception as e:
            print(f"Error embedding query: {e}")
            return []

    def embed_batch(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """Embed multiple texts at once."""
        try:
            result = self.client.embed(texts, model="voyage-3-lite", input_type=input_type)
            return result.embeddings
        except Exception as e:
            print(f"Error embedding batch: {e}")
            return []


embeddings_service = EmbeddingsService()
