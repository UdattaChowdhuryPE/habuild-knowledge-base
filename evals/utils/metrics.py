"""RAG evaluation metrics."""

from typing import List, Dict, Any


def hit_rate(results: List[Dict[str, Any]], expected_keywords: List[str]) -> bool:
    """
    Check if at least one result contains any of the expected keywords.
    Returns True if hit rate is >= 1/len(results) (i.e., at least one result is relevant).
    """
    if not expected_keywords or not results:
        return len(results) > 0 if not expected_keywords else False
    
    for result in results:
        content = (result.get('content') or '').lower()
        if any(keyword.lower() in content for keyword in expected_keywords):
            return True
    return False


def mrr(results: List[Dict[str, Any]], expected_keywords: List[str]) -> float:
    """
    Mean Reciprocal Rank: 1 / rank_of_first_relevant_result.
    Returns the reciprocal of the rank (1-indexed) of the first relevant result.
    Returns 0.0 if no relevant result found.
    """
    if not expected_keywords or not results:
        return 0.0
    
    for i, result in enumerate(results):
        content = (result.get('content') or '').lower()
        if any(keyword.lower() in content for keyword in expected_keywords):
            return 1.0 / (i + 1)
    return 0.0


def precision_at_k(results: List[Dict[str, Any]], expected_keywords: List[str], k: int = 5) -> float:
    """
    Precision@K: fraction of top-k results that contain expected keywords.
    """
    if not expected_keywords or not results:
        return 0.0
    
    top_k = results[:k]
    relevant_count = sum(
        1 for result in top_k
        if any(keyword.lower() in (result.get('content') or '').lower() 
               for keyword in expected_keywords)
    )
    return relevant_count / len(top_k) if top_k else 0.0


def location_leak(results: List[Dict[str, Any]], queried_location: str) -> float:
    """
    Fraction of results whose locations array does NOT contain the queried location.
    Returns 0.0 if no results or all results contain the queried location (good).
    Returns 1.0 if all results lack the queried location (bad — location bleed).
    """
    if not results:
        return 0.0
    
    leaked = 0
    for result in results:
        locations = result.get('locations') or []
        if queried_location not in locations:
            leaked += 1
    
    return leaked / len(results) if results else 0.0


def all_similarities_valid(results: List[Dict[str, Any]]) -> bool:
    """
    Check that all results have similarity scores in valid range (0, 1].
    """
    for result in results:
        sim = result.get('similarity')
        if sim is None or not (0 < sim <= 1):
            return False
    return True
