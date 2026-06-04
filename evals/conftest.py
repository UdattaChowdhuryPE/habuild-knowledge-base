"""Pytest configuration and fixtures for eval suite."""

import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load .env at test start
load_dotenv()


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Layer 1 tests (pure unit, no network)")
    config.addinivalue_line("markers", "integration: Layer 2 tests (needs Supabase + Voyage)")
    config.addinivalue_line("markers", "e2e: Layer 3 tests (needs all three APIs)")


@pytest.fixture(scope="session")
def sample_policy_text() -> str:
    """Load the committed sample HR policy."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_policy.txt"
    with open(fixture_path) as f:
        return f.read()


@pytest.fixture(scope="session")
def golden_qa_pairs() -> list:
    """Load golden QA pairs for evaluation."""
    fixture_path = Path(__file__).parent / "fixtures" / "golden_qa.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def has_supabase_env() -> bool:
    """Check if Supabase env vars are set."""
    return all([
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    ])


@pytest.fixture(scope="session")
def has_voyage_env() -> bool:
    """Check if Voyage API key is set."""
    return bool(os.getenv("VOYAGE_API_KEY"))


@pytest.fixture(scope="session")
def has_anthropic_env() -> bool:
    """Check if Anthropic API key is set."""
    return bool(os.getenv("ANTHROPIC_API_KEY"))


@pytest.fixture(scope="session")
def skip_if_no_integration_env(has_supabase_env, has_voyage_env):
    """Skip test if integration env vars missing."""
    def _skip():
        if not (has_supabase_env and has_voyage_env):
            pytest.skip("Missing Supabase or Voyage env vars")
    return _skip


@pytest.fixture(scope="session")
def skip_if_no_e2e_env(has_supabase_env, has_voyage_env, has_anthropic_env):
    """Skip test if e2e env vars missing."""
    def _skip():
        if not (has_supabase_env and has_voyage_env and has_anthropic_env):
            pytest.skip("Missing Supabase, Voyage, or Anthropic env vars")
    return _skip
