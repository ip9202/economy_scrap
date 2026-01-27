"""Test fixtures and configuration for pytest."""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_news_raw():
    """Sample raw news articles DataFrame."""
    return pd.DataFrame(
        {
            "query": ["한국은행 기준금리", "통화정책", "금리"],
            "published_at": [
                "2026-01-15T10:00:00",
                "2026-01-16T11:00:00",
                "2026-01-17T12:00:00",
            ],
            "title": [
                "한국은행, 기준금리 인상 결정",
                "통화정책 완화 기대",
                "금리 인하 가능성 논의",
            ],
            "summary": [
                "한국은행이 금리를 0.25%포인트 인상하기로 결정했습니다.",
                "시장에서는 통화정책 완화가 기대되고 있습니다.",
                "금리 인하 가능성에 대해 논의가 있습니다.",
            ],
            "google_url": [
                "https://news.google.com/articles/1",
                "https://news.google.com/articles/2",
                "https://news.google.com/articles/3",
            ],
        }
    )


@pytest.fixture
def sample_rate_series():
    """Sample rate series DataFrame."""
    return pd.DataFrame(
        {
            "date": [
                date(2026, 1, 1),
                date(2026, 1, 15),
                date(2026, 2, 1),
                date(2026, 2, 15),
            ],
            "value": [3.50, 3.75, 3.75, 3.50],
            "unit": ["%"] * 4,
            "name": ["한국은행 기준금리"] * 4,
            "source": ["ECOS"] * 4,
        }
    )


@pytest.fixture
def sample_news_scored(sample_news_raw):
    """Sample scored news articles DataFrame."""
    df = sample_news_raw.copy()
    df["text"] = df["title"] + " " + df["summary"]
    df["hawk_count"] = [1, 0, 0]  # Only first has "인상"
    df["dove_count"] = [0, 1, 1]  # Second and third have "완화", "인하"
    df["stance_score"] = df["hawk_count"] - df["dove_count"]
    return df


@pytest.fixture
def sample_news_daily(sample_news_scored):
    """Sample daily aggregated stance DataFrame."""
    return pd.DataFrame(
        {
            "date": [date(2026, 1, 15), date(2026, 1, 16), date(2026, 1, 17)],
            "n_articles": [1, 1, 1],
            "stance_mean": [1.0, -1.0, -1.0],
            "stance_sum": [1, -1, -1],
        }
    )


@pytest.fixture
def sample_events():
    """Sample events DataFrame."""
    return pd.DataFrame(
        {
            "date": [date(2026, 1, 15), date(2026, 2, 15)],
            "prev_value": [3.50, 3.75],
            "value": [3.75, 3.50],
            "diff": [0.25, -0.25],
            "event_type": ["raise", "cut"],
        }
    )


@pytest.fixture
def sample_event_study_table():
    """Sample event study table DataFrame."""
    data = []
    for event_type in ["raise", "cut"]:
        for day_offset in range(-14, 15):
            data.append(
                {
                    "event_date": date(2026, 1, 15),
                    "event_type": event_type,
                    "date": date(2026, 1, 15) + pd.Timedelta(days=day_offset),
                    "day_offset": day_offset,
                    "stance_mean": float(day_offset * 0.1),
                    "n_articles": 1,
                }
            )
    return pd.DataFrame(data)
