"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from ratestance.config import Settings


def test_settings_missing_api_key(tmp_path, monkeypatch):
    """Test that Settings raises error when API key is missing."""
    # Create a temporary empty .env file to avoid loading the project's .env
    empty_env = tmp_path / ".env"
    empty_env.write_text("# Empty env file\n")

    # Clear environment variable and use empty .env file
    monkeypatch.delenv("ECOS_API_KEY", raising=False)

    # Settings should fail validation when initialized without API key
    # Note: We use _env_file to override the default .env file location
    from pydantic_settings import SettingsConfigDict

    class TestSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=str(empty_env), env_file_encoding="utf-8", extra="ignore"
        )

    with pytest.raises(ValidationError, match="ECOS_API_KEY"):
        TestSettings()


def test_settings_default_api_key(monkeypatch):
    """Test that Settings accepts valid API key."""
    monkeypatch.setenv("ECOS_API_KEY", "test_api_key_123")
    config = Settings()
    assert config.ecod_api_key == "test_api_key_123"


def test_settings_months_back_validation():
    """Test months_back validation."""
    with pytest.raises(ValueError, match="Must be positive integer"):
        Settings(ecod_api_key="test_key", months_back=0)


def test_settings_event_window_days_validation():
    """Test event_window_days validation."""
    with pytest.raises(ValueError, match="Must be positive integer"):
        Settings(ecod_api_key="test_key", event_window_days=-1)


def test_settings_queries_default(monkeypatch):
    """Test default queries."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")
    config = Settings()
    assert len(config.queries) == 3
    assert "한국은행 기준금리" in config.queries


def test_settings_hawk_words_default(monkeypatch):
    """Test default hawk words."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")
    config = Settings()
    assert len(config.hawk_words) > 0
    assert "인상" in config.hawk_words


def test_settings_dove_words_default(monkeypatch):
    """Test default dove words."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")
    config = Settings()
    assert len(config.dove_words) > 0
    assert "인하" in config.dove_words


def test_settings_custom_values(monkeypatch):
    """Test custom configuration values."""
    monkeypatch.setenv("ECOS_API_KEY", "custom_key")
    config = Settings(
        months_back=3,
        event_window_days=7,
        max_items_per_query=50,
    )
    assert config.months_back == 3
    assert config.event_window_days == 7
    assert config.max_items_per_query == 50
