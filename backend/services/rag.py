import tiktoken
import re
from typing import List, Dict, Any
from .embeddings import embeddings_service
from .db import db


def _split_by_sentences(text: str) -> List[str]:
    """Split text on sentence boundaries (., !, ?) followed by whitespace."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def _extract_overlap_prefix(chunk: str, overlap_tokens: int, encoding) -> tuple[str, int]:
    """Extract the last N tokens of complete sentences from chunk as overlap prefix.
    
    Returns (overlap_text, overlap_token_count).
    """
    if not chunk.strip() or overlap_tokens <= 0:
        return "", 0
    
    sentences = _split_by_sentences(chunk)
    overlap_sents = []
    count = 0
    
    # Walk backwards through sentences, accumulating until we exceed overlap_tokens
    for sent in reversed(sentences):
        sent_toks = len(encoding.encode(sent))
        if count + sent_toks > overlap_tokens:
            break
        overlap_sents.insert(0, sent)
        count += sent_toks
    
    overlap_text = " ".join(overlap_sents)
    return overlap_text, count


def semantic_chunk_text(text: str, max_tokens: int = 500, overlap_tokens: int = 100) -> List[str]:
    """
    Split text into chunks respecting structural boundaries (paragraphs, sections).
    
    1. Splits on paragraph breaks (double newlines)
    2. Groups paragraphs into chunks staying under max_tokens
    3. If a single paragraph exceeds max_tokens, splits by sentences (never mid-sentence)
    4. Overlaps adjacent chunks: the last overlap_tokens worth of sentences from each chunk
       is prefixed to the next chunk for context continuity
    """
    if not text:
        return []

    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Split on paragraph boundaries (double newlines)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        para_tokens = len(encoding.encode(paragraph))
        
        # If paragraph alone exceeds max_tokens, split by sentences
        if para_tokens > max_tokens:
            # Flush current chunk first (with overlap)
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                overlap_text, overlap_toks = _extract_overlap_prefix(current_chunk.strip(), overlap_tokens, encoding)
                current_chunk = overlap_text + " " if overlap_text else ""
                current_tokens = overlap_toks
            
            # Split paragraph into sentences and group them
            sentences = _split_by_sentences(paragraph)
            for sentence in sentences:
                sent_tokens = len(encoding.encode(sentence))
                
                # If adding this sentence would exceed limit and we have content, flush (with overlap)
                if current_tokens + sent_tokens > max_tokens and current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    overlap_text, overlap_toks = _extract_overlap_prefix(current_chunk.strip(), overlap_tokens, encoding)
                    current_chunk = overlap_text + " " if overlap_text else ""
                    current_tokens = overlap_toks
                
                current_chunk += sentence + " "
                current_tokens += sent_tokens
        else:
            # Paragraph fits under max_tokens
            if current_tokens + para_tokens <= max_tokens:
                current_chunk += paragraph + "\n\n"
                current_tokens += para_tokens
            else:
                # Flush current chunk and start new one (with overlap)
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    overlap_text, overlap_toks = _extract_overlap_prefix(current_chunk.strip(), overlap_tokens, encoding)
                    current_chunk = overlap_text + " " if overlap_text else ""
                    current_tokens = overlap_toks
                else:
                    current_chunk = ""
                    current_tokens = 0
                current_chunk += paragraph + "\n\n"
                current_tokens += para_tokens
    
    # Flush any remaining content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
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
    chunks = semantic_chunk_text(text, max_tokens=500)

    # Embed all chunks
    embeddings = embeddings_service.embed_batch(chunks, input_type="document")

    # Prepare data for storage
    chunks_data = []
    for chunk_content, embedding in zip(chunks, embeddings):
        if embedding:  # Only store if embedding succeeded
            chunks_data.append({
                "source_id": source_id,
                "source_type": source_type,
                "source_title": source_title,
                "content": chunk_content,
                "embedding": embedding,
                "locations": locations,
            })

    # Store in database
    db.store_chunks(source_id, source_type, source_title, chunks_data)


def search_chunks(question: str, location: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed query and search for relevant chunks using vector similarity.
    Then rerank the top candidates using Voyage's reranker.
    """
    query_embedding = embeddings_service.embed_query(question)

    if not query_embedding:
        return []

    # Fetch more candidates than top_k to give reranker more options
    candidates = db.search_chunks_by_location(query_embedding, location, top_k=top_k * 4)

    if not candidates:
        return []

    # Extract chunk texts for reranking
    chunk_texts = [chunk.get("content", "") for chunk in candidates]
    
    # Rerank using Voyage's reranker
    reranked = embeddings_service.rerank(question, chunk_texts, top_k=top_k)
    
    if not reranked:
        # If reranking fails, fall back to vector search results
        return candidates[:top_k]
    
    # Reorder chunks by reranker scores
    reranked_chunks = [candidates[r["index"]] for r in reranked]
    
    return reranked_chunks


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
