"""
Backend interfaces and implementations for decision models.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import time


@dataclass
class DecisionRequest:
    """A decision request."""
    
    state: Dict[str, Any]
    questions: Dict[str, Dict[str, Any]]
    request_id: Optional[str] = None


@dataclass
class DecisionResponse:
    """A decision response."""
    
    answers: Dict[str, Dict[str, Any]]
    usage: Dict[str, int]
    routing: Optional[Dict[str, Any]] = None
    latency_ms: float = 0
    cost_usd: float = 0
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class BackendStats:
    """Backend usage statistics."""
    
    total_requests: int = 0
    total_cost_usd: float = 0
    total_latency_ms: float = 0
    errors: int = 0


class DecisionBackend(ABC):
    """Abstract base class for decision backends."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stats = BackendStats()
    
    @abstractmethod
    def predict(self, request: DecisionRequest) -> DecisionResponse:
        """Make a prediction for a single request."""
        pass
    
    def predict_batch(self, requests: List[DecisionRequest]) -> List[DecisionResponse]:
        """Make predictions for a batch of requests."""
        return [self.predict(req) for req in requests]
    
    def get_stats(self) -> BackendStats:
        """Get backend statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = BackendStats()
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get backend name."""
        pass


class RateLimiter:
    """Simple rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def acquire(self) -> bool:
        """Try to acquire a slot. Returns True if allowed."""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [t for t in self.requests if now - t < 60]
        
        if len(self.requests) < self.requests_per_minute:
            self.requests.append(now)
            return True
        return False
    
    def wait_time(self) -> float:
        """Get wait time in seconds until next slot is available."""
        if not self.requests:
            return 0
        now = time.time()
        oldest = self.requests[0]
        return max(0, 60 - (now - oldest))


class CostLedger:
    """Track and enforce cost limits."""
    
    def __init__(self, cap_usd: float = 10.0):
        self.cap_usd = cap_usd
        self.total_cost_usd = 0
    
    def add_cost(self, cost_usd: float):
        """Add cost to ledger."""
        self.total_cost_usd += cost_usd
    
    def is_under_cap(self) -> bool:
        """Check if still under cost cap."""
        return self.total_cost_usd < self.cap_usd
    
    def remaining(self) -> float:
        """Get remaining budget."""
        return max(0, self.cap_usd - self.total_cost_usd)
