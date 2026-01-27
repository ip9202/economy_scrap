"""Tests for Visualizer."""

from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from ratestance.visualizer import Visualizer


def test_visualizer_initialization(tmp_path):
    """Test Visualizer initialization."""
    visualizer = Visualizer(output_dir=str(tmp_path))
    assert visualizer.output_dir == tmp_path
    assert tmp_path.exists()


@patch("ratestance.visualizer.plots.plt.savefig")
@patch("ratestance.visualizer.plots.plt.close")
def test_visualizer_plot_timeseries_success(
    mock_close, mock_savefig, tmp_path, sample_news_daily, sample_events
):
    """Test successful time series plot generation."""
    visualizer = Visualizer(output_dir=str(tmp_path))
    visualizer.plot_timeseries(sample_news_daily, sample_events)

    # Verify plt.savefig was called
    mock_savefig.assert_called_once()
    mock_close.assert_called_once()


@patch("ratestance.visualizer.plots.plt.savefig")
@patch("ratestance.visualizer.plots.plt.close")
def test_visualizer_plot_event_study_success(
    mock_close, mock_savefig, tmp_path, sample_event_study_table
):
    """Test successful event study plot generation."""
    visualizer = Visualizer(output_dir=str(tmp_path))
    visualizer.plot_event_study(sample_event_study_table)

    # Verify plt.savefig was called
    mock_savefig.assert_called_once()
    mock_close.assert_called_once()


def test_visualizer_plot_timeseries_missing_columns_raises_error(tmp_path):
    """Test that missing columns raise ValueError."""
    visualizer = Visualizer(output_dir=str(tmp_path))

    invalid_daily = pd.DataFrame({"invalid": ["data"]})
    invalid_events = pd.DataFrame({"date": [date(2026, 1, 15)], "event_type": ["raise"]})

    with pytest.raises(ValueError, match="Missing required columns in daily_stance"):
        visualizer.plot_timeseries(invalid_daily, invalid_events)


def test_visualizer_plot_event_study_missing_columns_raises_error(tmp_path):
    """Test that missing columns raise ValueError."""
    visualizer = Visualizer(output_dir=str(tmp_path))

    invalid_data = pd.DataFrame({"invalid": ["data"]})

    with pytest.raises(ValueError, match="Missing required column"):
        visualizer.plot_event_study(invalid_data)
