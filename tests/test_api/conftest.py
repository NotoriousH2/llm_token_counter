import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "Hello, this is a test message for token counting."


@pytest.fixture
def sample_korean_text():
    """Sample Korean text for testing"""
    return "안녕하세요, 토큰 계산 테스트입니다."
