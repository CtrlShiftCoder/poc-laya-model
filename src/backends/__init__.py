"""
Backend factory and utilities.
"""
import os
from typing import Optional

from .base import DecisionBackend, CostLedger, RateLimiter
from .http import JevHTTPBackend, LayaHTTPBackend
from .laya_local import LayaLocalBackend


def create_backend(
    backend_type: str,
    config: Optional[dict] = None,
) -> DecisionBackend:
    """
    Create a decision backend.
    
    Args:
        backend_type: One of 'laya_local', 'laya_http', 'jev_http'
        config: Backend-specific configuration
    
    Returns:
        Configured backend instance
    
    Raises:
        ValueError: If backend type is unknown
        RuntimeError: If backend cannot be initialized
    """
    config = config or {}
    
    if backend_type == "laya_local":
        return LayaLocalBackend(config)
    
    elif backend_type == "laya_http":
        return LayaHTTPBackend(config)
    
    elif backend_type == "jev_http":
        api_key = os.getenv("TYPESAFE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Jev backend requires TYPESAFE_API_KEY environment variable"
            )
        return JevHTTPBackend(api_key=api_key, config=config)
    
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


__all__ = [
    "DecisionBackend",
    "LayaLocalBackend",
    "LayaHTTPBackend",
    "JevHTTPBackend",
    "RateLimiter",
    "CostLedger",
    "create_backend",
]
