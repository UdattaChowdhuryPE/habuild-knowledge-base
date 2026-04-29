import tiktoken
from typing import List, Dict, Any
from .embeddings import embeddings_service
from .db import db


def chunk_text(text: str, max_tokens: int = 500, overlap_tokens: int = 100) -> List[str]:
    """
    Split text into chunks with token-based sizing and overlap.
    """
    if not text:
        return []

    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    stride = max_tokens - overlap_tokens

    for i in range(0, len(tokens), stride):
        chunk_tokens = tokens[i : i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks


def index_document(
    source_id: str,
    source_type: str,
    source_title: str,
    text: str,
    locations: List[str]
) -> None:
    """
    Chunk document, embed chunks, and store in database.
    """
    chunks = chunk_text(text, max_tokens=500, overlap_tokens=100)

    # Embed all chunks
    embeddings = embeddings_service.embed_batch(chunks, input_type="document")

    # Prepare data for storage
    chunks_data = []
    for chunk_text, embedding in zip(chunks, embeddings):
        if embedding:  # Only store if embedding succeeded
            chunks_data.append({
                "source_id": source_id,
                "source_type": source_type,
                "source_title": source_title,
                "content": chunk_text,
                "embedding": embedding,
                "locations": locations,
            })

    # Store in database
    db.store_chunks(source_id, source_type, source_title, chunks_data)


def search_chunks(question: str, location: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed query and search for relevant chunks using vector similarity.
    """
    query_embedding = embeddings_service.embed_query(question)

    if not query_embedding:
        return []

    # Note: Supabase pgvector doesn't have a direct RPC for filtering by array contains.
    # We'll use a direct SQL query instead via the client.
    chunks = db.search_chunks_by_location(query_embedding, location, top_k)

    return chunks


def get_relevant_context(question: str, location: str, top_k: int = 5) -> str:
    """
    Search for relevant chunks and format them as context for the LLM.
    """
    chunks = search_chunks(question, location, top_k)

    if not chunks:
        return "No relevant documents found for your location."

    context = "Here are the relevant policy documents:\n\n"
    for i, chunk in enumerate(chunks, 1):
        source_title = chunk.get("source_title", "Unknown")
        content = chunk.get("content", "")
        context += f"[{i}] From: {source_title}\n{content}\n\n"

    return context
