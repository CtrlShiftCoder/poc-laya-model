"""
Local Laya backend using in-process Python API.
"""
import time
from typing import Any, Dict, Optional

from .base import DecisionBackend, DecisionRequest, DecisionResponse


class LayaLocalBackend(DecisionBackend):
    """Local Laya backend using Python API."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.agent = None
        self.router = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Laya model."""
        try:
            import laya
            
            # Use Router for multilingual support
            model = self.config.get("model", "multilingual")
            device = self.config.get("device", "cpu")
            
            if model == "router":
                self.router = laya.Router(default="multilingual", device=device)
            else:
                # Load specific model
                subfolder = None if model == "english" else model
                self.agent = laya.load(
                    "convaiinnovations/laya",
                    subfolder=subfolder,
                    device=device
                )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Laya: {e}")
    
    def predict(self, request: DecisionRequest) -> DecisionResponse:
        """Make a prediction."""
        start = time.time()
        
        try:
            runner = self.router if self.router else self.agent
            result = runner.predict(request.state, request.questions)
            
            latency_ms = (time.time() - start) * 1000
            
            # Extract answers and metadata
            answers = result.get("answers", {})
            usage = result.get("usage", {"input_tokens": 0, "output_tokens": 0})
            routing = result.get("routing")
            
            # Update stats
            self.stats.total_requests += 1
            self.stats.total_latency_ms += latency_ms
            
            return DecisionResponse(
                answers=answers,
                usage=usage,
                routing=routing,
                latency_ms=latency_ms,
                cost_usd=0,  # Local is free
                raw_response=result,
            )
        
        except Exception as e:
            self.stats.errors += 1
            raise RuntimeError(f"Prediction failed: {e}")
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.agent is not None or self.router is not None
    
    def get_name(self) -> str:
        """Get backend name."""
        return "laya_local"
