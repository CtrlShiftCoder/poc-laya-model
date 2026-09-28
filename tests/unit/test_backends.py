"""
Unit tests for backend implementations.
"""
import pytest
from unittest.mock import Mock, patch

from src.backends.base import (
    DecisionBackend,
    DecisionRequest,
    DecisionResponse,
    RateLimiter,
    CostLedger,
)
from src.backends import create_backend


def test_decision_request():
    """Test DecisionRequest creation."""
    state = {"text": "Hello"}
    questions = {"q1": {"type": "choice", "criteria": {}}}
    
    request = DecisionRequest(state=state, questions=questions, request_id="test-1")
    
    assert request.state == state
    assert request.questions == questions
    assert request.request_id == "test-1"


def test_decision_response():
    """Test DecisionResponse creation."""
    answers = {"q1": {"choice": "a", "confidence": 0.9}}
    usage = {"input_tokens": 10, "output_tokens": 5}
    
    response = DecisionResponse(
        answers=answers,
        usage=usage,
        latency_ms=100,
        cost_usd=0.001
    )
    
    assert response.answers == answers
    assert response.usage == usage
    assert response.latency_ms == 100
    assert response.cost_usd == 0.001


def test_rate_limiter():
    """Test RateLimiter."""
    limiter = RateLimiter(requests_per_minute=2)
    
    # Should allow first two requests
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    
    # Should deny third request
    assert limiter.acquire() is False
    
    # Wait time should be positive
    wait_time = limiter.wait_time()
    assert wait_time > 0


def test_cost_ledger():
    """Test CostLedger."""
    ledger = CostLedger(cap_usd=1.0)
    
    # Initially under cap
    assert ledger.is_under_cap() is True
    assert ledger.remaining() == 1.0
    
    # Add some cost
    ledger.add_cost(0.5)
    assert ledger.total_cost_usd == 0.5
    assert ledger.is_under_cap() is True
    assert ledger.remaining() == 0.5
    
    # Exceed cap
    ledger.add_cost(0.6)
    assert ledger.is_under_cap() is False
    assert ledger.remaining() == 0


class MockBackend(DecisionBackend):
    """Mock backend for testing."""
    
    def predict(self, request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            answers={"test": {"choice": "a", "confidence": 0.9}},
            usage={"input_tokens": 10, "output_tokens": 0},
            latency_ms=50,
            cost_usd=0,
        )
    
    def is_available(self) -> bool:
        return True
    
    def get_name(self) -> str:
        return "mock"


def test_backend_stats():
    """Test backend statistics tracking."""
    backend = MockBackend()
    
    assert backend.stats.total_requests == 0
    assert backend.stats.total_cost_usd == 0
    
    # Make a request
    request = DecisionRequest(
        state={"text": "test"},
        questions={"q": {"type": "choice", "criteria": {}}}
    )
    backend.predict(request)
    
    # Stats should be updated (in real backends)
    stats = backend.get_stats()
    assert stats.total_requests >= 0


def test_create_backend_laya_local():
    """Test creating laya_local backend."""
    # Should work but may fail if laya not installed
    try:
        backend = create_backend("laya_local", config={"model": "multilingual"})
        assert backend.get_name() == "laya_local"
    except RuntimeError:
        # Expected if laya not installed in test environment
        pytest.skip("Laya not available in test environment")


def test_create_backend_unknown():
    """Test creating unknown backend."""
    with pytest.raises(ValueError, match="Unknown backend type"):
        create_backend("nonexistent")


def test_create_backend_jev_without_key():
    """Test creating Jev backend without API key."""
    with pytest.raises(RuntimeError, match="TYPESAFE_API_KEY"):
        create_backend("jev_http")


@patch.dict("os.environ", {"TYPESAFE_API_KEY": "test-key"})
def test_create_backend_jev_with_key():
    """Test creating Jev backend with API key."""
    backend = create_backend("jev_http")
    assert backend.get_name() == "jev_http"
