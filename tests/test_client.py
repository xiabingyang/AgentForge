import pytest

from flowpilot.config import Config
from flowpilot.client import LLMClient


def test_config_defaults():
    config = Config()
    assert config.base_url
    assert config.temperature > 0
    assert config.max_tokens > 0


def test_client_init():
    config = Config(api_key="test-key")
    client = LLMClient(config)
    assert client.config.api_key == "test-key"
    assert "Bearer test-key" in client._client.headers["Authorization"]
