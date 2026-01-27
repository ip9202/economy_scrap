# Changelog

All notable changes to RateStance MVP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-27

### Added

#### Core Features
- **Data Collection Pipeline**
  - Google News RSS collector for economic news aggregation
  - ECOS OpenAPI client for Bank of Korea base rate data
  - Configurable date range and query parameters
  - Retry logic with exponential backoff for API resilience

- **Stance Scoring System**
  - Hawkish/dovish keyword detection algorithm
  - Configurable word lists for stance classification
  - Text scoring from article titles and summaries
  - Statistical logging of stance distribution

- **Daily Aggregation**
  - Time-series aggregation at daily frequency
  - Mean stance score calculation per day
  - Article count tracking per day

- **Event Detection**
  - Automatic rate change event detection
  - Event classification: raise, cut, hold
  - Precise event date identification from ECOS data

- **Event Study Analysis**
  - Event window analysis around rate changes
  - Cumulative stance calculation by event type
  - Statistical summary by day relative to event

- **Visualization**
  - Time series plot of daily news stance with event markers
  - Event study visualization by event type
  - Matplotlib-based high-quality plots

#### Configuration
- Pydantic-based configuration management
- Environment variable support via python-dotenv
- CLI argument parsing with overrides
- Comprehensive .env.example template

#### Logging
- Structured logging with Loguru
- File-based logs with rotation
- Detailed execution tracking
- Performance metrics logging

#### Developer Experience
- Comprehensive test suite (93.24% coverage, 50 tests)
- Type hints with strict mypy checking
- Ruff linting and Black formatting
- pytest integration with coverage reporting
- CLI entry point for easy execution

#### Documentation
- Complete README with installation and usage guide
- Research questions framing the analysis
- Interpretation guide for stance scores and event types
- API documentation with docstrings on all public functions

### Architecture

**Module Structure (10 files)**
```
src/ratestance/
├── config.py              # Configuration management
├── collector/
│   ├── news_collector.py  # RSS feed collection
│   └── ecos_client.py     # ECOS API client
├── scorer/
│   └── stance_scorer.py   # Hawkish/dovish scoring
├── aggregator/
│   └── daily_aggregator.py # Daily aggregation
├── analyzer/
│   ├── event_detector.py  # Rate change detection
│   └── event_study.py     # Event study analysis
├── visualizer/
│   └── plots.py           # Plot generation
├── pipeline.py            # Pipeline orchestration
└── cli.py                 # CLI entry point
```

**Test Coverage (16 files, 50 tests)**
- Unit tests for all modules
- Integration tests for pipeline
- Mock-based external dependency testing
- Edge case coverage

### Dependencies

**Core Runtime**
- requests>=2.31.0 - HTTP client
- feedparser>=6.0.10 - RSS feed parsing
- pandas>=2.1.0 - Data manipulation
- matplotlib>=3.8.0 - Visualization
- python-dotenv>=1.0.0 - Environment variables
- loguru>=0.7.0 - Logging
- tenacity>=8.2.0 - Retry logic
- pydantic>=2.0.0 - Configuration validation
- pydantic-settings>=2.0.0 - Settings management

**Development**
- pytest>=7.4.0 - Testing framework
- pytest-cov>=4.1.0 - Coverage reporting
- ruff>=0.1.0 - Linting
- mypy>=1.6.0 - Type checking
- black>=23.7.0 - Formatting
- pytest-mock>=3.12.0 - Mocking utilities

### Known Limitations

- **News Source**: Currently limited to Google News RSS feeds
- **Language Support**: Korean keywords only for stance detection
- **Event Window**: Fixed symmetric window around events (no pre/post differentiation)
- **Stance Detection**: Keyword-based only (no NLP or ML)
- **Geographic Focus**: Korea-specific (Bank of Korea ECOS API)

### Future Enhancements (Out of Scope for MVP)

- Multi-language news source support
- ML-based stance classification
- Real-time streaming analysis
- Web dashboard for visualization
- API server for programmatic access
- Database persistence for historical data

## [Unreleased]

### Planned
- Multi-central-bank support
- Advanced NLP stance detection
- Real-time monitoring dashboard
