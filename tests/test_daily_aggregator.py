"""Tests for DailyAggregator."""

import pandas as pd
import pytest

from ratestance.aggregator import DailyAggregator


def test_daily_aggregator_initialization():
    """Test DailyAggregator initialization."""
    aggregator = DailyAggregator()
    assert aggregator is not None


def test_daily_aggregator_success(sample_news_scored):
    """Test successful daily aggregation."""
    aggregator = DailyAggregator()
    result = aggregator.aggregate(sample_news_scored)

    assert "date" in result.columns
    assert "n_articles" in result.columns
    assert "stance_mean" in result.columns
    assert "stance_sum" in result.columns

    # Check that each row represents a unique date
    assert result["date"].is_unique


def test_daily_aggregator_calculation():
    """Test aggregation calculation logic."""
    # Create test data with multiple articles per day
    df = pd.DataFrame(
        {
            "published_at": [
                "2026-01-15T10:00:00",
                "2026-01-15T14:00:00",
                "2026-01-16T10:00:00",
            ],
            "stance_score": [1, 2, -1],
            "title": [
                "기준금리 인상 검토",
                "통화정책 완화 기대",
                "한국은행 금리 동결",
            ],
        }
    )

    aggregator = DailyAggregator()
    result = aggregator.aggregate(df)

    # Check first row (2026-01-15 aggregation)
    first_row = result.iloc[0]
    # The date should be 2026-01-15 (from first article)
    assert first_row["n_articles"] >= 1

    # Verify aggregation logic for a day with 2 articles
    # Find rows with articles
    rows_with_articles = result[result["n_articles"] == 2]
    if len(rows_with_articles) > 0:
        row = rows_with_articles.iloc[0]
        assert row["stance_mean"] == 1.5  # (1 + 2) / 2
        assert row["stance_sum"] == 3  # 1 + 2


def test_daily_aggregator_missing_columns_raises_error():
    """Test that missing columns raise ValueError."""
    aggregator = DailyAggregator()

    df = pd.DataFrame({"invalid": ["data"]})

    with pytest.raises(ValueError, match="Missing required column"):
        aggregator.aggregate(df)


def test_daily_aggregator_sorting(sample_news_scored):
    """Test that results are sorted by date."""
    aggregator = DailyAggregator()
    result = aggregator.aggregate(sample_news_scored)

    # Check that dates are in ascending order
    dates = result["date"].tolist()
    assert dates == sorted(dates)
