"""Tests for EventDetector."""

from datetime import date

import pandas as pd
import pytest

from ratestance.analyzer import EventDetector


def test_event_detector_initialization():
    """Test EventDetector initialization."""
    detector = EventDetector()
    assert detector is not None


def test_event_detector_detect_raise():
    """Test detection of rate raise events."""
    rate_series = pd.DataFrame(
        {
            "date": [date(2026, 1, 1), date(2026, 1, 15)],
            "value": [3.50, 3.75],
        }
    )

    detector = EventDetector()
    result = detector.detect(rate_series)

    assert len(result) == 1
    assert result.iloc[0]["event_type"] == "raise"
    assert result.iloc[0]["diff"] == 0.25


def test_event_detector_detect_cut():
    """Test detection of rate cut events."""
    rate_series = pd.DataFrame(
        {
            "date": [date(2026, 1, 1), date(2026, 1, 15)],
            "value": [3.75, 3.50],
        }
    )

    detector = EventDetector()
    result = detector.detect(rate_series)

    assert len(result) == 1
    assert result.iloc[0]["event_type"] == "cut"
    assert result.iloc[0]["diff"] == -0.25


def test_event_detector_detect_hold():
    """Test detection of rate hold events (should return empty since holds are excluded)."""
    rate_series = pd.DataFrame(
        {
            "date": [date(2026, 1, 1), date(2026, 1, 15)],
            "value": [3.50, 3.50],
        }
    )

    detector = EventDetector()
    result = detector.detect(rate_series)

    # Hold events are now excluded, so result should be empty
    assert len(result) == 0


def test_event_detector_multiple_events():
    """Test detection of multiple events (hold events excluded)."""
    rate_series = pd.DataFrame(
        {
            "date": [
                date(2026, 1, 1),
                date(2026, 1, 15),
                date(2026, 2, 1),
                date(2026, 2, 15),
            ],
            "value": [3.50, 3.75, 3.75, 3.50],
        }
    )

    detector = EventDetector()
    result = detector.detect(rate_series)

    # Only raise and cut events returned (hold at index 1->2 excluded)
    assert len(result) == 2
    assert result.iloc[0]["event_type"] == "raise"
    assert result.iloc[1]["event_type"] == "cut"


def test_event_detector_missing_columns_raises_error():
    """Test that missing columns raise ValueError."""
    detector = EventDetector()

    df = pd.DataFrame({"invalid": ["data"]})

    with pytest.raises(ValueError, match="Missing required column"):
        detector.detect(df)
