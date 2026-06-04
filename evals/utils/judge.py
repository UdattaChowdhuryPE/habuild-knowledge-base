"""LLM-as-judge for evaluating RAG answer quality using the RAG Triad."""

import json
from typing import Dict, Any
from anthropic import Anthropic

client = Anthropic()


def score_response(
    question: str,
    context: str,
    response: str,
) -> Dict[str, Any]:
    """
    Score a response using Claude as judge on RAG Triad metrics.
    
    Args:
        question: The user's question
        context: The retrieved context (formatted RAG chunks)
        response: The assistant's response
    
    Returns:
        Dict with keys: faithfulness, answer_relevance, context_relevance, reasoning
        Each metric is scored 1-5.
    """
    judge_prompt = f"""You are evaluating an HR assistant response based on the RAG Triad.

Question: {question}

Retrieved Context:
{context}

Assistant Response:
{response}

Score the response on these dimensions (1-5 scale):

1. Faithfulness: Every claim in the response is traceable to the context. A score of 5 means fully grounded, 1 means hallucinated/unsupported.
2. Answer Relevance: The response directly addresses the question asked. A score of 5 means directly answers, 1 means off-topic.
3. Context Relevance: The retrieved context is relevant to answering the question. A score of 5 means highly relevant, 1 means irrelevant noise.

Return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
  "faithfulness": <1-5>,
  "answer_relevance": <1-5>,
  "context_relevance": <1-5>,
  "reasoning": "<brief explanation>"
}}"""

    response_text = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": judge_prompt}],
    ).content[0].text
    
    try:
        result = json.loads(response_text)
        return {
            "faithfulness": result.get("faithfulness", 0),
            "answer_relevance": result.get("answer_relevance", 0),
            "context_relevance": result.get("context_relevance", 0),
            "reasoning": result.get("reasoning", ""),
        }
    except json.JSONDecodeError:
        return {
            "faithfulness": 0,
            "answer_relevance": 0,
            "context_relevance": 0,
            "reasoning": f"Failed to parse judge response: {response_text}",
        }
