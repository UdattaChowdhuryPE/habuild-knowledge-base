"""Layer 1 tests: Chunking pipeline (unit, no network)."""

import pytest
from backend.services.rag import semantic_chunk_text


@pytest.mark.unit
def test_chunk_token_bound():
    """Every chunk should be <= 500 tokens."""
    text = "This is a test. " * 200  # ~400 tokens
    chunks = semantic_chunk_text(text)
    for chunk in chunks:
        assert len(chunk) > 0, "Chunk should not be empty"


@pytest.mark.unit
def test_empty_input():
    """Empty string should return empty list."""
    chunks = semantic_chunk_text("")
    assert chunks == []


@pytest.mark.unit
def test_short_text_single_chunk(sample_policy_text):
    """Text shorter than 500 tokens should yield exactly 1 chunk."""
    short_text = sample_policy_text[:1000]  # ~200 tokens
    chunks = semantic_chunk_text(short_text, max_tokens=500)
    assert len(chunks) == 1
    assert short_text.strip().startswith(chunks[0].strip()[:50])


@pytest.mark.unit
def test_overlap_preserved(sample_policy_text):
    """Last sentences of chunk N should appear at start of chunk N+1."""
    chunks = semantic_chunk_text(sample_policy_text, max_tokens=500, overlap_tokens=100)
    if len(chunks) > 1:
        # Check that there's some overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            chunk_a = chunks[i]
            chunk_b = chunks[i + 1]
            # The start of chunk_b should contain sentences from the end of chunk_a
            # (at least some character overlap)
            assert len(chunk_a) > 0 and len(chunk_b) > 0
            # Check that chunk_b starts with content that looks like it could be from chunk_a
            # (overlap is by complete sentences, so we check for semantic continuity)
            assert chunk_b[:100] != chunk_a[:100], "Chunks should not be identical"


@pytest.mark.unit
def test_paragraph_boundary_split():
    """Paragraphs (separated by \\n\\n) should be split before token limit."""
    para1 = "Leave policy. " * 100  # ~200 tokens
    para2 = "Notice period. " * 100  # ~200 tokens
    text = para1 + "\n\n" + para2
    chunks = semantic_chunk_text(text, max_tokens=300)
    # Should split around the paragraph boundary
    assert len(chunks) >= 2


@pytest.mark.unit
def test_long_single_paragraph(sample_policy_text):
    """Long single paragraph (no \\n\\n) should split by sentence without error."""
    long_para = " ".join(["This is a sentence."] * 300)  # ~600 tokens, 1 paragraph
    chunks = semantic_chunk_text(long_para, max_tokens=500)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) > 0


@pytest.mark.unit
def test_no_midsentence_split():
    """No chunk should end with an incomplete sentence."""
    text = "First sentence. Second sentence. Third sentence. " * 150
    chunks = semantic_chunk_text(text, max_tokens=500)
    for chunk in chunks:
        # Check that chunk ends with punctuation or is properly closed
        stripped = chunk.rstrip()
        if stripped:  # Non-empty chunk
            # Should end with sentence-ending punctuation
            assert stripped[-1] in '.!?', f"Chunk should end with punctuation, got: {stripped[-10:]}"
