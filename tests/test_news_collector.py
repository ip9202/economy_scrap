"""Tests for NewsCollector."""

from datetime import date
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from ratestance.collector import NewsCollector


def test_news_collector_initialization():
    """Test NewsCollector initialization."""
    collector = NewsCollector()
    assert collector.user_agent == "RateStance/0.1.0"


@patch("ratestance.collector.news_collector.feedparser.parse")
def test_news_collector_collect_success(mock_parse):
    """Test successful news collection."""

    # Mock RSS feed response - create dict-like objects
    class MockEntry(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Support attribute access too
            for k, v in self.items():
                setattr(self, k, v)

        def get(self, key, default=None):
            return super().get(key, default)

    entry = MockEntry(
        {
            "title": "Test Article",
            "summary": "Test summary",
            "link": "https://news.google.com/article1",
            "published": "Mon, 15 Jan 2026 10:00:00 GMT",
        }
    )

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [entry]
    mock_parse.return_value = mock_feed

    collector = NewsCollector()
    result = collector.collect(
        queries=["test"],
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        max_items=10,
    )

    assert isinstance(result, pd.DataFrame)
    assert "query" in result.columns
    assert "published_at" in result.columns
    assert "title" in result.columns
    assert "summary" in result.columns
    assert "google_url" in result.columns


@patch("ratestance.collector.news_collector.feedparser.parse")
def test_news_collector_deduplication(mock_parse):
    """Test article deduplication."""

    class MockEntry(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for k, v in self.items():
                setattr(self, k, v)

        def get(self, key, default=None):
            return super().get(key, default)

    entry_data = {
        "title": "Duplicate Article",
        "summary": "Same content",
        "link": "https://news.google.com/article1",
        "published": "Mon, 15 Jan 2026 10:00:00 GMT",
    }

    entry1 = MockEntry(entry_data)
    entry2 = MockEntry(entry_data)

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [entry1, entry2]
    mock_parse.return_value = mock_feed

    collector = NewsCollector()
    result = collector.collect(
        queries=["test"],
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        max_items=10,
    )

    # Should deduplicate by google_url
    assert len(result) == 1


@patch("ratestance.collector.news_collector.feedparser.parse")
def test_news_collector_no_articles_raises_error(mock_parse):
    """Test that empty feed raises ValueError."""
    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = []
    mock_parse.return_value = mock_feed

    collector = NewsCollector()
    with pytest.raises(ValueError, match="No articles collected"):
        collector.collect(
            queries=["test"],
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )


@patch("ratestance.collector.news_collector.feedparser.parse")
def test_news_collector_date_filtering(mock_parse):
    """Test date range filtering."""

    class MockEntry(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for k, v in self.items():
                setattr(self, k, v)

        def get(self, key, default=None):
            return super().get(key, default)

    entry1 = MockEntry(
        {
            "title": "Article 1",
            "summary": "Summary 1",
            "link": "https://news.google.com/article1",
            "published": "Mon, 15 Jan 2026 10:00:00 GMT",
        }
    )

    entry2 = MockEntry(
        {
            "title": "Article 2",
            "summary": "Summary 2",
            "link": "https://news.google.com/article2",
            "published": "Mon, 15 Dec 2025 10:00:00 GMT",  # Outside range
        }
    )

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [entry1, entry2]
    mock_parse.return_value = mock_feed

    collector = NewsCollector()
    result = collector.collect(
        queries=["test"],
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    # Should only include article within date range
    assert len(result) == 1
    assert result.iloc[0]["title"] == "Article 1"
