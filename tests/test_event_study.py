"""Tests for EventStudy."""

from datetime import date

import pandas as pd
import pytest

from ratestance.analyzer import EventStudy


def test_event_study_initialization():
    """Test EventStudy initialization."""
    study = EventStudy()
    assert study is not None


def test_event_study_analyze_success(sample_events, sample_news_daily):
    """Test successful event study analysis."""
    study = EventStudy()
    result = study.analyze(
        events=sample_events,
        daily_stance=sample_news_daily,
        window_days=14,
    )

    assert "event_date" in result.columns
    assert "event_type" in result.columns
    assert "date" in result.columns
    assert "day_offset" in result.columns
    assert "stance_mean" in result.columns
    assert "n_articles" in result.columns

    # Check window range
    assert result["day_offset"].min() == -14
    assert result["day_offset"].max() == 14


def test_event_study_window_calculation():
    """Test event study window calculation."""
    events = pd.DataFrame(
        {
            "date": [date(2026, 1, 15)],
            "event_type": ["raise"],
        }
    )

    daily_stance = pd.DataFrame(
        {
            "date": [date(2026, 1, 15)],
            "stance_mean": [1.0],
            "n_articles": [1],
        }
    )

    study = EventStudy()
    result = study.analyze(
        events=events,
        daily_stance=daily_stance,
        window_days=7,
    )

    # Should have 15 rows per event (7 days before + event day + 7 days after)
    assert len(result) == 15

    # Check day_offset range
    assert result["day_offset"].min() == -7
    assert result["day_offset"].max() == 7


def test_event_study_missing_columns_raises_error():
    """Test that missing columns raise ValueError."""
    study = EventStudy()

    events = pd.DataFrame({"invalid": ["data"]})
    daily_stance = pd.DataFrame({"date": [date(2026, 1, 15)]})

    with pytest.raises(ValueError, match="Missing required columns in events"):
        study.analyze(events=events, daily_stance=daily_stance)


def test_event_study_nan_handling():
    """Test handling of missing stance data."""
    events = pd.DataFrame(
        {
            "date": [date(2026, 1, 15)],
            "event_type": ["raise"],
        }
    )

    daily_stance = pd.DataFrame(
        {
            "date": [date(2026, 1, 20)],  # Only one day of data
            "stance_mean": [1.0],
            "n_articles": [1],
        }
    )

    study = EventStudy()
    result = study.analyze(
        events=events,
        daily_stance=daily_stance,
        window_days=7,
    )

    # Should still have full window
    assert len(result) == 15

    # Most days should have NaN stance
    nan_count = result["stance_mean"].isna().sum()
    assert nan_count > 0
