"""Test configuration for pytest."""

import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(tmp_path_factory):
    """Setup test environment."""
    # Create temporary data directories
    tmp_dir = tmp_path_factory.mktemp("data")
    (tmp_dir / "uploads").mkdir()
    (tmp_dir / "outputs").mkdir()
    (tmp_dir / "chroma_db").mkdir()
    
    return tmp_dir


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4-test")
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "embedding-test")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")  # Reduce noise in tests
