"""Tests for CLI."""

from unittest.mock import Mock, patch

from ratestance.cli import main


@patch("ratestance.cli.Pipeline")
@patch("ratestance.cli.load_dotenv")
@patch("ratestance.cli.Settings")
def test_cli_success(mock_settings, mock_load_dotenv, mock_pipeline, monkeypatch):
    """Test successful CLI execution."""
    # Set required environment variable
    monkeypatch.setenv("ECOS_API_KEY", "test_key")

    # Mock settings
    mock_config = Mock()
    mock_settings.return_value = mock_config

    # Mock pipeline
    mock_pipeline_instance = Mock()
    mock_pipeline_instance.run.return_value = {
        "news_raw": Mock(__len__=Mock(return_value=100)),
        "events": Mock(__len__=Mock(return_value=5)),
        "event_study_table": Mock(__len__=Mock(return_value=100)),
    }
    mock_pipeline.return_value = mock_pipeline_instance

    # Mock sys.argv
    with patch("sys.argv", ["ratestance"]):
        result = main()

    assert result == 0
    mock_pipeline.assert_called_once_with(mock_config)
    mock_pipeline_instance.run.assert_called_once()


@patch("ratestance.cli.Pipeline")
@patch("ratestance.cli.load_dotenv")
@patch("ratestance.cli.Settings")
def test_cli_missing_api_key(mock_settings, mock_load_dotenv, mock_pipeline, monkeypatch):
    """Test CLI with missing API key."""
    # Remove API key
    monkeypatch.delenv("ECOS_API_KEY", raising=False)

    # Mock settings to raise validation error
    mock_settings.side_effect = Exception("ECOS_API_KEY environment variable is required")

    with patch("sys.argv", ["ratestance"]):
        result = main()

    assert result == 1


@patch("ratestance.cli.Pipeline")
@patch("ratestance.cli.load_dotenv")
@patch("ratestance.cli.Settings")
def test_cli_pipeline_failure(mock_settings, mock_load_dotenv, mock_pipeline, monkeypatch):
    """Test CLI with pipeline execution failure."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")

    mock_config = Mock()
    mock_settings.return_value = mock_config

    # Mock pipeline to raise exception
    mock_pipeline_instance = Mock()
    mock_pipeline_instance.run.side_effect = Exception("Pipeline failed")
    mock_pipeline.return_value = mock_pipeline_instance

    with patch("sys.argv", ["ratestance"]):
        result = main()

    assert result == 1
