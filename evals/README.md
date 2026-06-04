# Evaluation Suite for Habuild HR Policy Assistant

Comprehensive evaluation framework covering all three layers of the RAG pipeline: chunking, retrieval, and answer quality.

## Quick Start

```bash
# Install dev dependencies
uv sync --extra dev

# Run Layer 1 tests (unit, no API keys needed)
uv run pytest evals/ -m unit -v

# Run all tests (requires .env with all keys)
uv run pytest evals/ -v
```

## Test Layers

### Layer 1: Chunking (Unit Tests)

Location: `evals/test_chunking.py`

Tests the semantic chunking pipeline with synthetic data. Verifies:
- Token bound (≤ 500 tokens per chunk)
- Overlap correctness (100-token overlap between chunks)
- Proper sentence/paragraph boundary handling
- No mid-sentence splits

**Run:** `uv run pytest evals/ -m unit -v`

### Layer 2: Retrieval (Integration Tests)

Location: `evals/test_retrieval.py`

Tests vector search with live Supabase + Voyage. Requires `SUPABASE_*` and `VOYAGE_API_KEY` env vars.

Metrics:
- **Hit Rate@K**: Fraction of queries with ≥1 relevant result in top-5 (target: ≥0.8)
- **MRR**: Mean Reciprocal Rank of first relevant result (target: ≥0.5)
- **Precision@K**: Fraction of returned chunks that are relevant
- **Location Isolation**: Zero cross-location bleed (target: 0.0)

Tests also verify:
- Similarity scores are in valid range (0, 1]
- Bogus locations return empty results
- Reranker fallback works when embedding service fails

**Run:** `uv run pytest evals/ -m integration -v`

### Layer 3: Answer Quality (E2E Tests)

Location: `evals/test_answer_quality.py`

End-to-end evaluation using Claude-as-judge. Requires all API keys.

#### RAG Triad Metrics (Industry Standard)

| Metric | Description | Target |
|---|---|---|
| **Faithfulness** | Claims are grounded in retrieved context | Mean ≥ 3.5/5 |
| **Answer Relevance** | Response addresses the question | Mean ≥ 3.5/5 |
| **Context Relevance** | Retrieved chunks are relevant | Mean ≥ 3.5/5 |

#### Business-Specific Rules

- **Location Compliance**: Cross-location queries are refused (not answered with wrong location's policy)
- **Format Quality**: Policy answers use markdown formatting
- **Tool Use**: Employee lookup queries trigger tool calls (not hallucinated answers)

**Run:** `uv run pytest evals/ -m e2e -v`

## Test Markers

```bash
pytest evals/ -m unit                    # Layer 1 only (no network)
pytest evals/ -m integration             # Layer 2 (needs Supabase + Voyage)
pytest evals/ -m e2e                     # Layer 3 (needs all APIs)
pytest evals/ -m "integration or e2e"    # Layers 2 + 3 (requires all keys)
pytest evals/ -v                         # All tests
```

## Golden Data

### Fixtures

- `evals/fixtures/sample_policy.txt` — Committed synthetic HR policy (used for chunking tests)
- `evals/fixtures/golden_qa.json` — 5 golden QA pairs with expected behaviors

Golden QA behaviors:
- `"answer"` — Regular policy question, should get substantive answer
- `"refuse"` — Cross-location query, should be refused per location guard
- `"tool_use"` — Employee lookup, should trigger tool call

### Metrics & Utils

- `evals/utils/metrics.py` — `hit_rate()`, `mrr()`, `precision_at_k()`, `location_leak()`
- `evals/utils/judge.py` — Claude-as-judge scoring on RAG Triad

## Environment Variables

### Required for Full Suite

```bash
ANTHROPIC_API_KEY=...              # Claude API
VOYAGE_API_KEY=...                 # Voyage embeddings + reranker
SUPABASE_URL=...                   # Supabase project URL
SUPABASE_ANON_KEY=...              # Supabase anon key
SUPABASE_SERVICE_ROLE_KEY=...      # Supabase service role key
```

### Optional

If env vars are missing, integration and e2e tests auto-skip gracefully (safe for CI).

## Output

Tests provide:
- Per-metric scores (faithfulness, relevance, etc.)
- Mean scores across the golden set
- Reasoning from the judge
- Location isolation checks

## Extending Evals

### Add Golden QA Pairs

Edit `evals/fixtures/golden_qa.json`:

```json
{
  "question": "...",
  "location": "Gurugram",
  "expected_keywords": ["keyword1", "keyword2"],
  "expected_behavior": "answer|refuse|tool_use",
  "description": "..."
}
```

### Add New Tests

Create a new test file in `evals/`:
- Prefix with `test_` (e.g., `test_custom.py`)
- Decorate with `@pytest.mark.unit|integration|e2e`
- Use fixtures: `skip_if_no_integration_env`, `skip_if_no_e2e_env`

## Troubleshooting

**Tests skip without running:**
Check that `.env` file is in the project root with all required keys. conftest.py loads it at test start.

**Judge scores are low:**
This usually means retrieved context is not relevant, or the response doesn't ground claims. Check:
1. Are golden questions actually answerable by the current policy documents?
2. Are policies indexed in Supabase with correct location tags?
3. Does reranker recognize the query semantics?

**Location isolation fails:**
Location filtering in `match_chunks_by_location` RPC may have stale data. Verify chunks table has proper `locations` arrays.
