import os
import time
import voyageai
from typing import List, Dict, Any


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
        """Embed multiple texts at once, with retry on rate limit (free tier: 3 RPM)."""
        for attempt in range(3):
            try:
                result = self.client.embed(texts, model="voyage-3-lite", input_type=input_type)
                return result.embeddings
            except Exception as e:
                msg = str(e)
                print(f"Error embedding batch: {e}")
                # Rate limit: wait 20s and retry (free tier allows 3 RPM)
                if attempt < 2 and ("rate" in msg.lower() or "429" in msg or "payment" in msg.lower()):
                    time.sleep(20)
                    continue
                return []
        return []

    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rerank documents by relevance to the query using Voyage's reranker."""
        try:
            result = self.client.rerank(query, documents, model="rerank-2", top_k=top_k)
            return [{"index": r.index, "score": r.relevance_score} for r in result.results]
        except Exception as e:
            print(f"Error reranking: {e}")
            return []


embeddings_service = EmbeddingsService()
