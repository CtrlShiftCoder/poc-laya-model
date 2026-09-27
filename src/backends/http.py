"""
HTTP backend for Laya (laya-serve) and Jev (TypeSafe API).
"""
import time
from typing import Any, Dict, Optional

import httpx

from .base import DecisionBackend, DecisionRequest, DecisionResponse


class HTTPBackend(DecisionBackend):
    """Base class for HTTP-based backends."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(config)
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        self.client = httpx.Client(timeout=self.timeout)
    
    def predict(self, request: DecisionRequest) -> DecisionResponse:
        """Make a prediction via HTTP."""
        start = time.time()
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "state": request.state,
            "questions": request.questions,
        }
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code == 401:
                    raise RuntimeError("Authentication failed (401)")
                elif response.status_code == 403:
                    raise RuntimeError("Access forbidden (403)")
                elif response.status_code == 429:
                    raise RuntimeError("Rate limit exceeded (429)")
                
                response.raise_for_status()
                
                latency_ms = (time.time() - start) * 1000
                result = response.json()
                
                # Extract response fields
                answers = result.get("answers", {})
                usage = result.get("usage", {"input_tokens": 0, "output_tokens": 0})
                routing = result.get("routing")
                
                # Estimate cost (Jev pricing: $0.001 per request, Laya is free)
                cost_usd = 0.001 if "typesafe" in self.endpoint else 0
                
                # Update stats
                self.stats.total_requests += 1
                self.stats.total_latency_ms += latency_ms
                self.stats.total_cost_usd += cost_usd
                
                return DecisionResponse(
                    answers=answers,
                    usage=usage,
                    routing=routing,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    raw_response=result,
                )
            
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        self.stats.errors += 1
        raise RuntimeError(f"All {self.max_retries} attempts failed: {last_error}")
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            response = self.client.get(
                self.endpoint.replace("/v1/systemone", "/health"),
                timeout=5,
            )
            return response.status_code == 200
        except:
            return False
    
    def __del__(self):
        """Clean up HTTP client."""
        self.client.close()


class LayaHTTPBackend(HTTPBackend):
    """HTTP backend for laya-serve."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        endpoint = config.get("endpoint", "http://localhost:8000/v1/systemone")
        super().__init__(endpoint=endpoint, config=config)
    
    def get_name(self) -> str:
        return "laya_http"


class JevHTTPBackend(HTTPBackend):
    """HTTP backend for Jev (TypeSafe API)."""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        endpoint = config.get("endpoint", "https://api.typesafe.ai/v1/systemone")
        super().__init__(endpoint=endpoint, api_key=api_key, config=config)
    
    def get_name(self) -> str:
        return "jev_http"
