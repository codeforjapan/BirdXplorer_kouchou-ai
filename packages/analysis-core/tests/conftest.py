"""Shared pytest configuration for the analysis-core unit test suite (excludes tests/e2e).

analysis_core.core.orchestration.validate_api_keys() and analysis_core.services.llm
both call dotenv.load_dotenv() to read a real .env file from disk. Left alone, that
couples these tests' pass/fail outcome to whatever .env happens to exist on the
machine running them, instead of to the test's own explicit setup. Cut that coupling
by neutralizing both call sites and providing a deterministic fallback API key.

tests/e2e/ has its own conftest.py that loads a real .env on purpose (it needs a real
key to make live API calls); this fixture doesn't touch it since e2e is only collected
when explicitly targeted.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def isolate_from_real_dotenv(monkeypatch):
    monkeypatch.setattr("analysis_core.core.orchestration.load_dotenv", lambda *a, **k: False)
    monkeypatch.setattr("analysis_core.services.llm.load_dotenv", lambda *a, **k: False)
    if not os.environ.get("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
