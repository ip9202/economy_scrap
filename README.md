# RateStance MVP

Automated data pipeline for analyzing monetary policy news tone and its relationship with central bank rate decisions.

## Overview

RateStance MVP collects economic news from Google News RSS and Bank of Korea base rates from ECOS OpenAPI, then performs event study analysis to understand news sentiment dynamics around rate change events.

## Research Questions

- **RQ1**: Does news tone change lead rate events?
- **RQ2**: How long does tone change persist after events?
- **RQ3**: Do raise/hold/cut events have different tone reactions?

## Installation

### Prerequisites

- Python 3.11 or higher
- ECOS API key (get from https://ecos.bok.or.kr/api/)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd economy_scrap

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and add your ECOS_API_KEY
```

## Usage

### Basic Usage

```bash
# Run pipeline with default settings (6 months back, 14-day event window)
ratestance

# Or using Python module
python -m ratestance.cli --months-back 6 --event-window 14
```

### Custom Parameters

```bash
# Analyze last 3 months with 7-day event window
ratestance --months-back 3 --event-window 7
```

## Outputs

### Data Files (data/)

- **news_raw.csv**: Raw RSS feed articles
- **news_scored.csv**: Articles with stance scores
- **news_daily.csv**: Daily aggregated stance metrics
- **rate_series.csv**: Bank of Korea base rate time series
- **events.csv**: Detected rate change events
- **event_study_table.csv**: Event study analysis results

### Visualizations (outputs/)

- **news_stance_timeseries.png**: Time series of daily news stance
- **event_study.png**: Event study visualization by event type

### Logs (logs/)

- **ratestance_YYYYMMDD.log**: Pipeline execution logs

## Interpretation

### Stance Scores

- **Positive score (> 0)**: Hawkish stance (favoring rate increases)
- **Negative score (< 0)**: Dovish stance (favoring rate decreases)
- **Zero score (= 0)**: Neutral or no stance indicators

### Event Types

- **raise**: Central bank increased the base rate
- **cut**: Central bank decreased the base rate
- **hold**: Central bank kept the base rate unchanged

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=src/ratestance --cov-report=html

# Run specific test file
pytest tests/test_news_collector.py
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/ratestance --strict

# Formatting
black src/ tests/
```

## Project Structure

```
src/ratestance/
├── config.py              # Configuration management
├── collector/             # Data collection modules
│   ├── news_collector.py  # RSS feed collection
│   └── ecos_client.py     # ECOS API client
├── scorer/                # Text scoring modules
│   └── stance_scorer.py   # Hawkish/dovish scoring
├── aggregator/            # Data aggregation modules
│   └── daily_aggregator.py # Daily aggregation
├── analyzer/              # Analysis modules
│   ├── event_detector.py  # Rate change event detection
│   └── event_study.py     # Event study analysis
├── visualizer/            # Visualization modules
│   └── plots.py           # Plot generation
├── pipeline.py            # Pipeline orchestration
└── cli.py                 # CLI entry point
```

## License

MIT License

## Acknowledgments

- Bank of Korea ECOS Open API
- Google News RSS feeds
