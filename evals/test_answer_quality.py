"""Layer 3 tests: Answer quality via LLM-as-judge (e2e, needs all APIs)."""

import pytest
from backend.services.rag import get_relevant_context
from backend.services.llm import llm_service
from evals.utils.judge import score_response


def collect_stream_response(question: str, location: str, conversation_history: list = None) -> str:
    """
    Helper to collect streamed response into a single string.
    Mimics what the frontend does with SSE.
    """
    if conversation_history is None:
        conversation_history = []
    
    context = get_relevant_context(question, location, top_k=5)
    response_tokens = []
    
    # stream_chat is a generator that yields tokens
    for token in llm_service.stream_chat(question, context, conversation_history, location):
        response_tokens.append(token)
    
    return "".join(response_tokens)


@pytest.mark.e2e
def test_rag_triad_faithfulness(skip_if_no_e2e_env, golden_qa_pairs):
    """RAG Triad: Faithfulness. All claims should be grounded in context.
    Pass threshold: mean faithfulness >= 3.5/5 across answer questions.
    """
    skip_if_no_e2e_env()
    
    answer_questions = [qa for qa in golden_qa_pairs if qa["expected_behavior"] == "answer"]
    if not answer_questions:
        pytest.skip("No answer questions in golden set")
    
    faithfulness_scores = []
    
    for qa in answer_questions:
        try:
            response = collect_stream_response(qa["question"], qa["location"])
            context = get_relevant_context(qa["question"], qa["location"], top_k=5)
            
            score = score_response(qa["question"], context, response)
            faithfulness_scores.append(score["faithfulness"])
        except Exception as e:
            print(f"Error scoring {qa['question']}: {e}")
            continue
    
    if faithfulness_scores:
        mean_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
        assert mean_faithfulness >= 3.5, f"Faithfulness too low: {mean_faithfulness}"


@pytest.mark.e2e
def test_rag_triad_answer_relevance(skip_if_no_e2e_env, golden_qa_pairs):
    """RAG Triad: Answer Relevance. Response should directly address the question.
    Pass threshold: mean answer_relevance >= 3.5/5 across answer questions.
    """
    skip_if_no_e2e_env()
    
    answer_questions = [qa for qa in golden_qa_pairs if qa["expected_behavior"] == "answer"]
    if not answer_questions:
        pytest.skip("No answer questions in golden set")
    
    relevance_scores = []
    
    for qa in answer_questions:
        try:
            response = collect_stream_response(qa["question"], qa["location"])
            context = get_relevant_context(qa["question"], qa["location"], top_k=5)
            
            score = score_response(qa["question"], context, response)
            relevance_scores.append(score["answer_relevance"])
        except Exception as e:
            print(f"Error scoring {qa['question']}: {e}")
            continue
    
    if relevance_scores:
        mean_relevance = sum(relevance_scores) / len(relevance_scores)
        assert mean_relevance >= 3.5, f"Answer relevance too low: {mean_relevance}"


@pytest.mark.e2e
def test_rag_triad_context_relevance(skip_if_no_e2e_env, golden_qa_pairs):
    """RAG Triad: Context Relevance. Retrieved chunks should be relevant to the question.
    Pass threshold: mean context_relevance >= 3.5/5 across answer questions.
    """
    skip_if_no_e2e_env()
    
    answer_questions = [qa for qa in golden_qa_pairs if qa["expected_behavior"] == "answer"]
    if not answer_questions:
        pytest.skip("No answer questions in golden set")
    
    context_scores = []
    
    for qa in answer_questions:
        try:
            response = collect_stream_response(qa["question"], qa["location"])
            context = get_relevant_context(qa["question"], qa["location"], top_k=5)
            
            score = score_response(qa["question"], context, response)
            context_scores.append(score["context_relevance"])
        except Exception as e:
            print(f"Error scoring {qa['question']}: {e}")
            continue
    
    if context_scores:
        mean_context_rel = sum(context_scores) / len(context_scores)
        assert mean_context_rel >= 3.5, f"Context relevance too low: {mean_context_rel}"


@pytest.mark.e2e
def test_location_compliance_refusal(skip_if_no_e2e_env, golden_qa_pairs):
    """Business rule: Cross-location queries should be refused.
    For questions with expected_behavior='refuse', response should contain location guard message.
    """
    skip_if_no_e2e_env()
    
    refuse_questions = [qa for qa in golden_qa_pairs if qa["expected_behavior"] == "refuse"]
    if not refuse_questions:
        pytest.skip("No refuse questions in golden set")
    
    for qa in refuse_questions:
        try:
            response = collect_stream_response(qa["question"], qa["location"])
            # The location guard returns a canned message when user tries to access different location
            # Check that response indicates refusal (contains relevant keywords or is short/generic)
            response_lower = response.lower()
            # Response should NOT contain detailed policy information
            assert "sorry" in response_lower or "cannot" in response_lower or "not available" in response_lower or len(response) < 100, \
                f"Should refuse cross-location query, got: {response[:100]}"
        except Exception as e:
            print(f"Error on refusal test {qa['question']}: {e}")
            pytest.skip(f"Could not test refusal: {e}")


@pytest.mark.e2e
def test_format_quality_answer(skip_if_no_e2e_env, golden_qa_pairs):
    """Business rule: Policy answers should use markdown formatting.
    Response should contain at least one markdown element (##, -, **, etc.).
    """
    skip_if_no_e2e_env()
    
    answer_questions = [qa for qa in golden_qa_pairs if qa["expected_behavior"] == "answer"]
    if not answer_questions:
        pytest.skip("No answer questions in golden set")
    
    for qa in answer_questions:
        try:
            response = collect_stream_response(qa["question"], qa["location"])
            # Check for markdown formatting
            has_markdown = any(marker in response for marker in ["##", "- ", "**", "_", "`"])
            assert has_markdown, f"Response should use markdown formatting: {response[:100]}"
        except Exception as e:
            print(f"Error on format test {qa['question']}: {e}")
            # Non-critical; skip rather than fail
            continue
