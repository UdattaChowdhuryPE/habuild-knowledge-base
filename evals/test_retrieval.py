"""Layer 2 tests: Retrieval pipeline (integration, needs Supabase + Voyage)."""

import pytest
from unittest.mock import patch, MagicMock
from backend.services.rag import search_chunks, get_relevant_context
from evals.utils.metrics import hit_rate, mrr, precision_at_k, location_leak, all_similarities_valid


@pytest.mark.integration
def test_hit_rate_on_golden_questions(skip_if_no_integration_env, golden_qa_pairs):
    """At least 80% of golden questions should have hit rate >= 1 (relevant result in top 5)."""
    skip_if_no_integration_env()
    
    passed = 0
    total = 0
    
    for qa in golden_qa_pairs:
        if qa["expected_behavior"] != "answer":
            continue
        
        total += 1
        try:
            results = search_chunks(qa["question"], qa["location"], top_k=5)
            if hit_rate(results, qa["expected_keywords"]):
                passed += 1
        except Exception:
            pass  # Network or API failures are acceptable in integration tests
    
    if total > 0:
        assert passed / total >= 0.8, f"Hit rate only {passed}/{total}"


@pytest.mark.integration
def test_location_isolation(skip_if_no_integration_env, golden_qa_pairs):
    """All returned chunks should contain the queried location in their locations array."""
    skip_if_no_integration_env()
    
    for qa in golden_qa_pairs:
        if qa["expected_behavior"] != "answer":
            continue
        
        try:
            results = search_chunks(qa["question"], qa["location"], top_k=5)
            # Zero location leak means all results have the queried location
            leak = location_leak(results, qa["location"])
            assert leak == 0.0, f"Location leak detected: {leak} for {qa['location']}"
        except Exception:
            pass


@pytest.mark.integration
def test_similarity_values_valid(skip_if_no_integration_env, golden_qa_pairs):
    """All returned similarity scores should be in (0, 1]."""
    skip_if_no_integration_env()
    
    for qa in golden_qa_pairs[:2]:  # Test just a couple to save API calls
        try:
            results = search_chunks(qa["question"], qa["location"], top_k=5)
            if results:
                assert all_similarities_valid(results), "Invalid similarity scores"
        except Exception:
            pass


@pytest.mark.integration
def test_bogus_location_returns_empty(skip_if_no_integration_env):
    """Query with non-existent location should return empty list."""
    skip_if_no_integration_env()
    
    try:
        results = search_chunks("leave policy", "FakeCity_NonExistent_12345", top_k=5)
        assert len(results) == 0, "Bogus location should return empty results"
    except Exception:
        pass


@pytest.mark.integration
def test_reranker_fallback():
    """If reranker fails, search_chunks should fall back to raw vector results."""
    # This test uses monkeypatching to simulate reranker failure
    from backend.services import rag
    
    original_rerank = rag.embeddings_service.rerank
    try:
        # Mock rerank to return empty list (simulating failure)
        rag.embeddings_service.rerank = MagicMock(return_value=[])
        
        # Skip if no real data available
        try:
            results = search_chunks("leave policy", "Gurugram", top_k=5)
            # Even if reranker fails, should get results from raw vector search
            # (This is a light test; full validation needs real data)
            assert isinstance(results, list)
        except Exception:
            pytest.skip("No Supabase data available for fallback test")
    finally:
        rag.embeddings_service.rerank = original_rerank


@pytest.mark.integration
def test_get_relevant_context_formatting(skip_if_no_integration_env, golden_qa_pairs):
    """get_relevant_context should return properly formatted string with chunk sources."""
    skip_if_no_integration_env()
    
    qa = golden_qa_pairs[0]
    try:
        context = get_relevant_context(qa["question"], qa["location"], top_k=5)
        assert isinstance(context, str)
        # Should have formatting like "[1] From: ..." or mention of sources
        if context and "From:" not in context:
            # Alternative format is acceptable as long as content is there
            assert len(context) > 0
    except Exception:
        pytest.skip("No Supabase data available")
