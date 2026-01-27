# RateStance MVP - Implementation Plan

## TAG BLOCK

```
TAG: SPEC-RATESTANCE-001
PROJECT: RateStance MVP
PHASE: Plan
DOCUMENT: plan.md
STATUS: Ready for Implementation
CREATED: 2026-01-27
```

---

## 1. Milestones

### 1.1 Priority Level: High (Primary Goals)

**Milestone 1: Project Foundation**
- Objective: Set up project structure and configuration
- Dependencies: None
- Tasks:
  - Create src/ratestance module structure
  - Set up pyproject.toml with dependencies
  - Configure pytest with coverage plugin
  - Create .env.example for ECOS_API_KEY
  - Initialize Git repository with .gitignore
- Success Criteria: Project structure complete, tests can run

**Milestone 2: Data Collection**
- Objective: Implement RSS and ECOS data collectors
- Dependencies: Milestone 1
- Tasks:
  - Implement NewsCollector class with feedparser
  - Implement EcosClient class with requests
  - Add retry logic and error handling
  - Create unit tests for collectors
  - Add integration tests with mocked APIs
- Success Criteria: Can collect news and rate data

**Milestone 3: Scoring and Aggregation**
- Objective: Implement stance scoring and daily aggregation
- Dependencies: Milestone 2
- Tasks:
  - Implement StanceScorer with keyword counting
  - Implement DailyAggregator with pandas groupby
  - Add data validation at each stage
  - Create unit tests for scoring logic
  - Create unit tests for aggregation logic
- Success Criteria: Can score articles and aggregate daily

**Milestone 4: Event Detection and Analysis**
- Objective: Implement event detection and event study
- Dependencies: Milestone 3
- Tasks:
  - Implement EventDetector with diff logic
  - Implement EventStudy with window-based analysis
  - Add defensive parsing for ECOS API
  - Create unit tests for event detection
  - Create unit tests for event study
- Success Criteria: Can detect events and analyze tone dynamics

**Milestone 5: Visualization and Pipeline**
- Objective: Implement plotting and pipeline orchestration
- Dependencies: Milestone 4
- Tasks:
  - Implement Visualizer with matplotlib/plotly
  - Implement Pipeline orchestration class
  - Create CLI interface with argparse
  - Add comprehensive logging
  - Create end-to-end integration tests
- Success Criteria: Can run full pipeline from CLI

### 1.2 Priority Level: Medium (Secondary Goals)

**Milestone 6: Documentation and Examples**
- Objective: Complete documentation and usage examples
- Dependencies: Milestone 5
- Tasks:
  - Write comprehensive README.md
  - Add docstrings to all public functions
  - Create example notebook with pipeline run
  - Add interpretation guide for outputs
  - Create CHANGELOG.md
- Success Criteria: New users can run pipeline independently

### 1.3 Priority Level: Low (Optional Goals)

**Milestone 7: Performance and Caching**
- Objective: Add performance optimizations
- Dependencies: Milestone 5
- Tasks:
  - Implement ECOS API response caching
  - Add concurrent RSS feed collection
  - Optimize pandas operations
  - Add performance benchmarks
- Success Criteria: Pipeline runs 50% faster

---

## 2. Technical Approach

### 2.1 Architecture Pattern

**Pattern**: Layered Architecture with Pipeline orchestration

**Layers**:
1. **Collector Layer**: Data collection from external sources
2. **Scorer Layer**: Text processing and stance scoring
3. **Aggregator Layer**: Time-series aggregation
4. **Analyzer Layer**: Event detection and study
5. **Visualizer Layer**: Plot generation
6. **Pipeline Layer**: Orchestration of all layers

**Rationale**: Clear separation of concerns enables independent testing and maintenance

### 2.2 Module Design

**Config Management** (config.py):
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    ecod_api_key: str
    months_back: int = 6
    event_window_days: int = 14
    queries: list[str] = ["한국은행 기준금리", "통화정책", "금리"]
    hawk_words: list[str] = ["인상", "긴축", "물가압력", "과열", "억제", "경계", "매파"]
    dove_words: list[str] = ["인하", "완화", "둔화", "부양", "하방", "지원", "비둘기"]
    max_items_per_query: int = 100

    class Config:
        env_file = ".env"
```

**Pipeline Orchestration** (pipeline.py):
```python
class Pipeline:
    def __init__(self, config: Settings):
        self.config = config
        self.news_collector = NewsCollector()
        self.ecos_client = EcosClient()
        self.stance_scorer = StanceScorer()
        self.daily_aggregator = DailyAggregator()
        self.event_detector = EventDetector()
        self.event_study = EventStudy()
        self.visualizer = Visualizer()

    def run(self) -> dict:
        """Execute full pipeline and return results."""
        # Stage 1: Calculate date range
        date_range = self._calculate_date_range()

        # Stage 2: Collect news
        news_raw = self.news_collector.collect(...)

        # Stage 3: Score articles
        news_scored = self.stance_scorer.score(...)

        # Stage 4: Aggregate daily
        news_daily = self.daily_aggregator.aggregate(...)

        # Stage 5: Collect rates
        rate_series = self.ecos_client.fetch_base_rates(...)

        # Stage 6: Detect events
        events = self.event_detector.detect(...)

        # Stage 7: Event study
        event_study_table = self.event_study.analyze(...)

        # Stage 8: Visualize
        self.visualizer.plot_timeseries(...)
        self.visualizer.plot_event_study(...)

        return {
            "news_raw": news_raw,
            "news_scored": news_scored,
            "news_daily": news_daily,
            "rate_series": rate_series,
            "events": events,
            "event_study_table": event_study_table,
        }
```

### 2.3 Error Handling Strategy

**Retry Logic**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(url: str):
    return requests.get(url, timeout=30)
```

**Graceful Degradation**:
- Log warnings for non-critical failures
- Continue pipeline with available data
- Provide clear error messages for showstoppers

**Data Validation**:
```python
def validate_news_raw(df: pd.DataFrame) -> None:
    required_columns = ["query", "published_at", "title", "summary", "google_url"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    if df["google_url"].duplicated().any():
        logger.warning("Duplicate URLs detected, deduplicating...")
        df = df.drop_duplicates(subset=["google_url"])
```

### 2.4 Testing Strategy

**Unit Tests** (pytest):
- Test each module in isolation
- Mock external dependencies (APIs, file system)
- Achieve 85%+ code coverage

**Integration Tests**:
- Test pipeline stages with real data
- Use fixture data for reproducibility
- Validate data flow between modules

**Characterization Tests**:
- Capture current behavior for data collectors
- Ensure behavior preservation during refactoring
- Use pytest-md plugin for snapshot testing

**Test Structure**:
```
tests/
├── unit/
│   ├── test_news_collector.py
│   ├── test_ecos_client.py
│   ├── test_stance_scorer.py
│   ├── test_daily_aggregator.py
│   ├── test_event_detector.py
│   ├── test_event_study.py
│   └── test_visualizer.py
├── integration/
│   ├── test_pipeline.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_news.csv
    └── sample_rates.csv
```

### 2.5 Logging Strategy

**Structured Logging** (loguru):
```python
from loguru import logger

logger.remove()  # Remove default handler
logger.add(
    "logs/ratestance_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
)

# Usage in pipeline
logger.info("Starting pipeline", extra={"months_back": config.months_back})
logger.success("Pipeline completed successfully")
logger.error("API request failed", extra={"url": url, "status": status_code})
```

---

## 3. Implementation Sequence

### Phase 1: Foundation (Days 1-2)

**Step 1.1**: Create project structure
```
src/ratestance/
├── __init__.py
├── config.py
├── collector/
│   ├── __init__.py
│   ├── news_collector.py
│   └── ecos_client.py
├── scorer/
│   ├── __init__.py
│   └── stance_scorer.py
├── aggregator/
│   ├── __init__.py
│   └── daily_aggregator.py
├── analyzer/
│   ├── __init__.py
│   ├── event_detector.py
│   └── event_study.py
├── visualizer/
│   ├── __init__.py
│   └── plots.py
├── pipeline.py
└── cli.py
```

**Step 1.2**: Configure dependencies in pyproject.toml
```toml
[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.0.0"
requests = "^2.31.0"
feedparser = "^6.0.10"
python-dotenv = "^1.0.0"
pydantic = "^2.0.0"
loguru = "^0.7.0"
matplotlib = "^3.7.0"
plotly = "^5.18.0"
tenacity = "^8.2.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
pytest-md = "^0.3.0"
ruff = "^0.1.0"
black = "^23.7.0"
mypy = "^1.5.0"
```

**Step 1.3**: Create test configuration
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src/ratestance
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
```

### Phase 2: Data Collection (Days 3-4)

**Step 2.1**: Implement NewsCollector
- Use feedparser for RSS parsing
- Filter articles by date range
- Deduplicate by google_url
- Save to news_raw.csv

**Step 2.2**: Implement EcosClient
- Use requests for HTTP calls
- Add retry logic with tenacity
- Parse JSON response defensively
- Save to rate_series.csv

**Step 2.3**: Write tests
- Mock RSS feed responses
- Mock ECOS API responses
- Test error scenarios
- Validate data schemas

### Phase 3: Scoring and Aggregation (Days 5-6)

**Step 3.1**: Implement StanceScorer
- Combine title and summary into text
- Count hawkish keywords (case-insensitive)
- Count dovish keywords (case-insensitive)
- Calculate stance_score = hawk_count - dove_count
- Save to news_scored.csv

**Step 3.2**: Implement DailyAggregator
- Group by date
- Calculate mean stance_score
- Calculate sum stance_score
- Count articles
- Save to news_daily.csv

**Step 3.3**: Write tests
- Test keyword counting logic
- Test edge cases (empty text, no keywords)
- Test aggregation with multiple articles
- Validate output schemas

### Phase 4: Event Detection and Analysis (Days 7-8)

**Step 4.1**: Implement EventDetector
- Calculate diff from rate_series
- Classify events (raise/hold/cut)
- Handle missing data points
- Save to events.csv

**Step 4.2**: Implement EventStudy
- Merge events with news_daily
- Create window around each event (±event_window_days)
- Calculate day_offset relative to event
- Save to event_study_table.csv

**Step 4.3**: Write tests
- Test event detection with synthetic rate series
- Test hold-only scenario
- Test event study window calculation
- Validate output schemas

### Phase 5: Visualization and Pipeline (Days 9-10)

**Step 5.1**: Implement Visualizer
- Plot news_stance_timeseries.png
  - X-axis: date
  - Y-axis: stance_mean
  - Mark rate change events with vertical lines
- Plot event_study.png
  - X-axis: day_offset
  - Y-axis: stance_mean
  - Facet by event_type (raise/hold/cut)

**Step 5.2**: Implement Pipeline
- Orchestrate all stages
- Add progress logging
- Handle errors gracefully
- Validate outputs

**Step 5.3**: Implement CLI
```python
def main():
    parser = argparse.ArgumentParser(description="RateStance MVP Pipeline")
    parser.add_argument("--months-back", type=int, default=6)
    parser.add_argument("--event-window", type=int, default=14)
    parser.add_argument("--output-dir", type=str, default="outputs")
    args = parser.parse_args()

    config = Settings(months_back=args.months_back, event_window_days=args.event_window)
    pipeline = Pipeline(config)
    results = pipeline.run()

    logger.info("Pipeline completed successfully")
```

**Step 5.4**: Write tests
- End-to-end pipeline test with fixture data
- Test CLI argument parsing
- Test visualization output files

### Phase 6: Documentation (Days 11-12)

**Step 6.1**: Write README.md
- Project overview
- Installation instructions
- Usage examples
- Interpretation guide

**Step 6.2**: Add docstrings
- Google-style docstrings for all public functions
- Type hints for all parameters
- Examples in docstrings

**Step 6.3**: Create CHANGELOG.md
- Version history
- Feature additions
- Bug fixes

---

## 4. Risk Management

### 4.1 Technical Risks

**Risk**: ECOS API rate limiting
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Implement exponential backoff
  - Cache API responses
  - Provide fallback to manual data entry

**Risk**: RSS feed structure changes
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Defensive parsing with error handling
  - Schema validation before processing
  - Clear error messages for debugging

**Risk**: Insufficient test data
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Create fixture data from sample runs
  - Use synthetic data for edge cases
  - Mock external dependencies

### 4.2 Schedule Risks

**Risk**: Underestimated complexity
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Prioritize High-priority milestones first
  - Defer Low-priority optimizations
  - Daily progress tracking

**Risk**: API access delays
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**:
  - Apply for ECOS API key early
  - Use mocked responses for development
  - Document API key acquisition process

---

## 5. Quality Assurance

### 5.1 Code Quality Standards

**Linting** (ruff):
```bash
ruff check src/ tests/
ruff format src/ tests/
```

**Type Checking** (mypy):
```bash
mypy src/ratestance --strict
```

**Formatting** (black):
```bash
black src/ tests/
```

**Import Sorting** (isort):
```bash
isort src/ tests/
```

### 5.2 Test Coverage Requirements

**Minimum Coverage**: 85%
**Enforcement**: pytest-cov --cov-fail-under=85

**Coverage Targets by Module**:
- collector: 90% (external dependencies)
- scorer: 95% (core logic)
- aggregator: 90% (data transformation)
- analyzer: 90% (complex logic)
- visualizer: 80% (plotting code)
- pipeline: 85% (orchestration)

### 5.3 CI/CD Integration

**GitHub Actions Workflow**:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check src/ tests/
      - run: poetry run mypy src/ratestance
      - run: poetry run pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 6. Success Criteria

### 6.1 Functional Criteria

- [ ] Pipeline runs from start to finish without errors
- [ ] All 6 output CSV files are generated
- [ ] 2 visualization plots are generated
- [ ] months_back parameter affects data period
- [ ] event_window_days parameter affects analysis window

### 6.2 Quality Criteria

- [ ] Test coverage ≥ 85%
- [ ] Zero ruff errors
- [ ] Zero mypy errors
- [ ] All tests passing
- [ ] Documentation complete

### 6.3 Usability Criteria

- [ ] CLI interface is intuitive
- [ ] Error messages are clear and actionable
- [ ] README enables first-time users to succeed
- [ ] Code is readable and maintainable

---

## 7. Handoff to Run Phase

### 7.1 Pre-Run Checklist

- [ ] All Milestones 1-5 completed
- [ ] Test coverage meets 85% threshold
- [ ] All quality gates passing
- [ ] Documentation reviewed and approved
- [ ] ECOS_API_KEY acquired and tested

### 7.2 Known Limitations

- Korean news only (no multi-language support)
- RSS feeds only (no article body scraping)
- CSV output only (no database persistence)
- CLI only (no web UI)

### 7.3 Future Enhancements

Out of scope for MVP but identified for future iterations:
- Real-time streaming processing
- ML-based stance classification
- Multi-central bank comparison
- Interactive dashboard with Plotly Dash
- REST API for programmatic access
- PostgreSQL persistence layer

---

**Plan Status**: Ready for DDD Implementation
**Next Command**: /moai:2-run SPEC-RATESTANCE-001
**Estimated Complexity**: Medium (6 core modules, ~2000 lines of code)

---

*This plan follows DDD ANALYZE-PRESERVE-IMPROVE methodology and prioritizes TRUST 5 quality principles.*
