"""Tests for Pipeline integration."""

from datetime import date
from unittest.mock import Mock, patch

import pandas as pd

from ratestance.config import Settings
from ratestance.pipeline import Pipeline


@patch("ratestance.pipeline.NewsCollector")
@patch("ratestance.pipeline.EcosClient")
@patch("ratestance.pipeline.Visualizer")
def test_pipeline_initialization(mock_visualizer, mock_ecos, mock_news, monkeypatch):
    """Test Pipeline initialization."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")

    config = Settings()
    pipeline = Pipeline(config)

    assert pipeline.config == config


@patch("ratestance.pipeline.NewsCollector")
@patch("ratestance.pipeline.EcosClient")
@patch("ratestance.pipeline.StanceScorer")
@patch("ratestance.pipeline.DailyAggregator")
@patch("ratestance.pipeline.EventDetector")
@patch("ratestance.pipeline.EventStudy")
@patch("ratestance.pipeline.Visualizer")
def test_pipeline_run_success(
    mock_visualizer,
    mock_event_study,
    mock_event_detector,
    mock_aggregator,
    mock_scorer,
    mock_ecos,
    mock_news,
    monkeypatch,
    sample_news_raw,
    sample_rate_series,
):
    """Test successful pipeline execution."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")

    config = Settings()

    # Mock all dependencies
    mock_news_instance = Mock()
    mock_news_instance.collect.return_value = sample_news_raw
    mock_news.return_value = mock_news_instance

    mock_ecos_instance = Mock()
    mock_ecos_instance.fetch_base_rates.return_value = sample_rate_series
    mock_ecos.return_value = mock_ecos_instance

    mock_scorer_instance = Mock()
    mock_scorer_instance.score.return_value = sample_news_raw
    mock_scorer.return_value = mock_scorer_instance

    mock_aggregator_instance = Mock()
    mock_aggregator_instance.aggregate.return_value = pd.DataFrame(
        {
            "date": [date(2026, 1, 15)],
            "n_articles": [1],
            "stance_mean": [1.0],
            "stance_sum": [1],
        }
    )
    mock_aggregator.return_value = mock_aggregator_instance

    mock_event_detector_instance = Mock()
    mock_event_detector_instance.detect.return_value = pd.DataFrame(
        {
            "date": [date(2026, 1, 15)],
            "prev_value": [3.50],
            "value": [3.75],
            "diff": [0.25],
            "event_type": ["raise"],
        }
    )
    mock_event_detector.return_value = mock_event_detector_instance

    mock_event_study_instance = Mock()
    mock_event_study_instance.analyze.return_value = pd.DataFrame(
        {
            "event_date": [date(2026, 1, 15)],
            "event_type": ["raise"],
            "date": [date(2026, 1, 15)],
            "day_offset": [0],
            "stance_mean": [1.0],
            "n_articles": [1],
        }
    )
    mock_event_study.return_value = mock_event_study_instance

    mock_visualizer_instance = Mock()
    mock_visualizer.return_value = mock_visualizer_instance

    # Run pipeline
    pipeline = Pipeline(config)
    results = pipeline.run()

    # Verify all stages were called
    mock_news_instance.collect.assert_called_once()
    mock_ecos_instance.fetch_base_rates.assert_called_once()
    mock_scorer_instance.score.assert_called_once()
    mock_aggregator_instance.aggregate.assert_called_once()
    mock_event_detector_instance.detect.assert_called_once()
    mock_event_study_instance.analyze.assert_called_once()

    # Verify results
    assert "news_raw" in results
    assert "news_scored" in results
    assert "news_daily" in results
    assert "rate_series" in results
    assert "events" in results
    assert "event_study_table" in results


@patch("ratestance.pipeline.NewsCollector")
@patch("ratestance.pipeline.EcosClient")
def test_pipeline_calculate_date_range(mock_ecos, mock_news, monkeypatch):
    """Test date range calculation."""
    monkeypatch.setenv("ECOS_API_KEY", "test_key")

    config = Settings(months_back=6)
    pipeline = Pipeline(config)

    start_date, end_date = pipeline._calculate_date_range()

    assert isinstance(end_date, date)
    assert isinstance(start_date, date)
    assert (end_date - start_date).days >= 180  # Approximately 6 months
