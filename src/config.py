"""
Configuration management using pydantic-settings.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendConfig(BaseSettings):
    """Backend-specific configuration."""
    
    endpoint: str
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""
    
    requests_per_minute: int = 60
    cost_cap_usd: float = 10.0


class LayaModelConfig(BaseSettings):
    """Laya model configuration."""
    
    default_model: str = "multilingual"
    device: str = "cpu"
    cache_dir: str = ".cache/models"


class MetricsConfig(BaseSettings):
    """Metrics calculation configuration."""
    
    ece_bins: int = 10
    bootstrap_iterations: int = 1000
    confidence_level: float = 0.95


class DatasetConfig(BaseSettings):
    """Dataset configuration for PoC 1."""
    
    name: str
    subset: Optional[str] = None
    sample_size: int = 100
    task: str


class PoC1Config(BaseSettings):
    """PoC 1 benchmark configuration."""
    
    datasets: List[Dict[str, Any]]
    output_dir: str = "reports/poc1"


class PoC2Config(BaseSettings):
    """PoC 2 triage configuration."""
    
    synthetic_dataset: str
    categories: List[str]
    urgency_levels: int = 3
    confidence_threshold: float = 0.75
    output_dir: str = "reports/poc2"


class Config(BaseSettings):
    """Global configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="LAYA_EVAL_",
        env_nested_delimiter="__",
    )
    
    laya_http: Optional[BackendConfig] = None
    jev_http: Optional[BackendConfig] = None
    rate_limit: Optional[RateLimitConfig] = None
    laya: Optional[LayaModelConfig] = None
    metrics: Optional[MetricsConfig] = None
    poc1: Optional[PoC1Config] = None
    poc2: Optional[PoC2Config] = None
    
    # Environment variables
    typesafe_api_key: Optional[str] = Field(None, alias="TYPESAFE_API_KEY")


def load_config(config_path: str = "config/default.yaml") -> Config:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    return Config(**data)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance, loading if needed."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
