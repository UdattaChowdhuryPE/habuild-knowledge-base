import os
import time
import voyageai
import structlog
from typing import List, Dict, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from backend.observability import get_tracer

log = structlog.get_logger(__name__)
tracer = get_tracer(__name__)


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
            log.error("embed_document.failed", exc_info=True)
            return []

    def embed_query(self, text: str) -> List[float]:
        """Embed a query for semantic search."""
        with tracer.start_as_current_span("voyage.embed_query") as span:
            try:
                result = self.client.embed([text], model="voyage-3-lite", input_type="query")
                embedding = result.embeddings[0]
                span.set_attribute("embedding.dim", len(embedding))
                return embedding
            except Exception as e:
                log.error("embed_query.failed", exc_info=True)
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return []

    def embed_batch(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """Embed multiple texts at once, with retry on rate limit (free tier: 3 RPM)."""
        with tracer.start_as_current_span("voyage.embed_batch") as span:
            span.set_attribute("batch_size", len(texts))
            span.set_attribute("input_type", input_type)
            for attempt in range(3):
                try:
                    result = self.client.embed(texts, model="voyage-3-lite", input_type=input_type)
                    log.info(
                        "embed_batch.complete",
                        batch_size=len(texts),
                        dim=len(result.embeddings[0]) if result.embeddings else 0,
                    )
                    return result.embeddings
                except Exception as e:
                    msg = str(e)
                    log.error("embed_batch.failed", attempt=attempt, exc_info=True)
                    # Rate limit: wait 20s and retry (free tier allows 3 RPM)
                    if attempt < 2 and ("rate" in msg.lower() or "429" in msg or "payment" in msg.lower()):
                        log.warning(
                            "embed_batch.rate_limit_retry",
                            attempt=attempt + 1,
                            wait_s=20,
                        )
                        time.sleep(20)
                        continue
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    return []
            return []

    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rerank documents by relevance to the query using Voyage's reranker."""
        with tracer.start_as_current_span("voyage.rerank") as span:
            span.set_attribute("rerank.candidate_count", len(documents))
            span.set_attribute("rerank.top_k", top_k)
            try:
                result = self.client.rerank(query, documents, model="rerank-2", top_k=top_k)
                reranked = [{"index": r.index, "score": r.relevance_score} for r in result.results]
                log.info(
                    "rerank.complete",
                    candidate_count=len(documents),
                    returned=len(reranked),
                )
                return reranked
            except Exception as e:
                log.error("rerank.failed", exc_info=True)
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return []


embeddings_service = EmbeddingsService()
