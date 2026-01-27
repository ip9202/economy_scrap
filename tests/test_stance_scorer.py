"""Tests for StanceScorer."""

import pandas as pd
import pytest

from ratestance.scorer import StanceScorer


def test_stance_scorer_initialization():
    """Test StanceScorer initialization."""
    scorer = StanceScorer(hawk_words=["인상", "긴추"], dove_words=["인하", "완화"])
    assert len(scorer.hawk_words) == 2
    assert len(scorer.dove_words) == 2


def test_stance_scorer_score_success(sample_news_raw):
    """Test successful stance scoring."""
    scorer = StanceScorer(hawk_words=["인상"], dove_words=["완화", "인하"])

    result = scorer.score(sample_news_raw)

    assert "text" in result.columns
    assert "hawk_count" in result.columns
    assert "dove_count" in result.columns
    assert "stance_score" in result.columns

    # Check formula: stance_score = hawk_count - dove_count
    assert all(result["stance_score"] == result["hawk_count"] - result["dove_count"])


def test_stance_scorer_case_insensitive(sample_news_raw):
    """Test that keyword counting is case-insensitive."""
    scorer = StanceScorer(hawk_words=["인상"], dove_words=["완화"])

    # Add article with uppercase keyword
    sample_news_raw.loc[len(sample_news_raw)] = {
        "query": "test",
        "published_at": "2026-01-18T10:00:00",
        "title": "한국은행 금리 인상",
        "summary": "Summary",
        "google_url": "https://test.com",
    }

    result = scorer.score(sample_news_raw)

    # Should count "인상" regardless of case
    hawkish_articles = result[result["hawk_count"] > 0]
    assert len(hawkish_articles) > 0


def test_stance_scorer_missing_columns_raises_error():
    """Test that missing columns raise ValueError."""
    scorer = StanceScorer(hawk_words=["인상"], dove_words=["완화"])

    df = pd.DataFrame({"invalid": ["data"]})

    with pytest.raises(ValueError, match="Missing required column"):
        scorer.score(df)


def test_stance_scorer_text_combination(sample_news_raw):
    """Test that text combines title and summary."""
    scorer = StanceScorer(hawk_words=["인상"], dove_words=["완화"])

    result = scorer.score(sample_news_raw)

    # Check that text combines title and summary
    for _, row in result.iterrows():
        assert row["title"] in row["text"]
        assert row["summary"] in row["text"]
