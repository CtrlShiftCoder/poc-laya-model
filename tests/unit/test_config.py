"""
Unit tests for configuration management.
"""
import pytest
from pathlib import Path
import yaml
import tempfile

from src.config import Config, load_config


def test_config_defaults():
    """Test Config with defaults."""
    config = Config()
    assert config.typesafe_api_key is None


def test_load_config_from_yaml():
    """Test loading config from YAML file."""
    # Create temporary config file
    config_data = {
        "laya": {
            "default_model": "multilingual",
            "device": "cpu",
        },
        "rate_limit": {
            "requests_per_minute": 60,
            "cost_cap_usd": 10.0,
        }
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        assert config.laya.default_model == "multilingual"
        assert config.rate_limit.cost_cap_usd == 10.0
    finally:
        Path(temp_path).unlink()


def test_load_config_file_not_found():
    """Test loading non-existent config file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")
