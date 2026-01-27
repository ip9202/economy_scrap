# RateStance MVP - Core Specification

## TAG BLOCK

```
TAG: SPEC-RATESTANCE-001
PROJECT: RateStance MVP
STATUS: Completed
PRIORITY: High
ASSIGNED: TBD
CREATED: 2026-01-27
DOMAIN: Data Science Pipeline
TECH_STACK: Python 3.11+, pandas, requests, feedparser, matplotlib, pytest
```

---

## 1. Environment

### 1.1 Project Context

**Project Name**: RateStance MVP
**Project Type**: Data Science Pipeline (Python)
**Working Directory**: /Users/ip9202/develop/vibe/economy_scrap
**Development Mode**: DDD (Domain-Driven Development)

### 1.2 Problem Statement

Central banks' monetary policy decisions significantly impact financial markets, but understanding the relationship between news sentiment and policy actions remains challenging. Analysts need systematic tools to:

1. Quantify economic news tone (hawkish vs dovish stance)
2. Analyze tone dynamics around rate change events
3. Identify leading or lagging indicators in news sentiment

### 1.3 Research Questions

- **RQ1**: Does news tone change lead rate events?
- **RQ2**: How long does tone change persist after events?
- **RQ3**: Do raise/hold/cut events have different tone reactions?

### 1.4 Data Sources

**ECOS OpenAPI** (https://ecos.bok.or.kr/api/):
- Authentication: API key required (ECOS_API_KEY env var)
- Target: "한국은행 기준금리" (Base Rate)
- Strategy: Use KeyStatisticList endpoint with defensive parsing

**Google News RSS**:
- URL: https://news.google.com/rss/search?q={QUERY}&hl=ko&gl=KR&ceid=KR:ko
- Fields: published_at, title, summary, google_url, query
- Deduplication: by google_url, then (title, date)

---

## 2. Assumptions

### 2.1 Technical Assumptions

- ECOS API provides consistent response structure for KeyStatisticList endpoint
- Google News RSS remains accessible without authentication
- Python 3.11+ runtime environment is available
- Internet connectivity is stable during data collection

### 2.2 Business Assumptions

- Korean economic news contains sufficient hawkish/dovish keywords
- Base rate changes occur at least quarterly (historical pattern)
- News tone correlates with monetary policy stance
- 6-month historical window provides sufficient event samples

### 2.3 Data Assumptions

- ECOS API returns daily base rate data points
- RSS feeds provide article publication dates
- Text content (title + summary) contains stance indicators
- At least 100 news articles can be collected per 6-month period

---

## 3. Requirements (EARS Format)

### 3.1 Ubiquitous Requirements (Always Active)

**REQ-001**: The system SHALL validate all input parameters before pipeline execution.
- Rationale: Prevent pipeline failures from invalid configuration
- Verification: Parameter validation tests in test suite

**REQ-002**: The system SHALL log all pipeline stages with timestamps.
- Rationale: Debugging and reproducibility
- Verification: Log output contains stage markers

**REQ-003**: The system SHALL handle network errors gracefully with retry logic.
- Rationale: External API calls are failure-prone
- Verification: Error handling tests with mocked failures

**REQ-004**: The system SHALL validate data integrity at each pipeline stage.
- Rationale: Ensure data quality before analysis
- Verification: Data validation tests

### 3.2 Event-Driven Requirements (Trigger-Response)

**REQ-005**: WHEN pipeline execution starts, the system SHALL calculate the date range (today - months_back).
- Input: months_back parameter (default=6)
- Output: start_date, end_date
- Rationale: Define temporal scope for data collection

**REQ-006**: WHEN date range is calculated, the system SHALL collect news from RSS feeds.
- Input: queries list, date range
- Output: news_raw.csv
- Constraints: Filter by date, deduplicate by google_url
- Rationale: Gather news corpus for tone analysis

**REQ-007**: WHEN news collection completes, the system SHALL score articles for stance.
- Input: news_raw.csv, hawk_words, dove_words
- Output: news_scored.csv (hawk_count, dove_count, stance_score)
- Formula: stance_score = hawk_count - dove_count
- Rationale: Quantify tone as numerical score

**REQ-008**: WHEN articles are scored, the system SHALL aggregate to daily level.
- Input: news_scored.csv
- Output: news_daily.csv (date, n_articles, stance_mean, stance_sum)
- Rationale: Enable time-series analysis

**REQ-009**: WHEN daily aggregation completes, the system SHALL collect base rates from ECOS API.
- Input: date range, ECOS_API_KEY
- Output: rate_series.csv (date, value, unit, name, source)
- Strategy: Auto-discover "한국은행 기준금리" with defensive parsing
- Rationale: Obtain official policy rate data

**REQ-010**: WHEN rate series is collected, the system SHALL detect rate change events.
- Input: rate_series.csv
- Output: events.csv (date, prev_value, value, diff, event_type)
- Event Types: raise (diff > 0), cut (diff < 0), hold (diff == 0)
- Rationale: Identify policy events for study

**REQ-011**: WHEN events are detected, the system SHALL perform event study analysis.
- Input: events.csv, news_daily.csv, event_window_days (default=14)
- Output: event_study_table.csv (event_date, event_type, date, day_offset, stance_mean, n_articles)
- Window: ±event_window_days around each event
- Rationale: Analyze tone dynamics around events

**REQ-012**: WHEN event study completes, the system SHALL generate visualization plots.
- Output: news_stance_timeseries.png, event_study.png
- Rationale: Visual communication of findings

### 3.3 State-Driven Requirements (Conditional Behavior)

**REQ-013**: IF ECOS_API_KEY environment variable is missing, the system SHALL terminate with clear error message.
- Rationale: Fail fast on missing credentials
- Verification: Environment variable tests

**REQ-014**: IF RSS feed returns insufficient results (< 10 articles), the system SHALL log warning but continue.
- Rationale: Graceful degradation for sparse data
- Verification: Edge case tests

**REQ-015**: IF no rate change events (raise/cut) are detected, the system SHALL still generate event study with hold events only.
- Rationale: Handle periods of policy stability
- Verification: Hold-only scenario tests

**REQ-016**: IF ECOS API response structure changes, the system SHALL fall back to defensive parsing with regex.
- Rationale: Robustness against API changes
- Verification: Malformed response tests

### 3.4 Unwanted Requirements (Prohibited Behavior)

**REQ-017**: The system SHALL NOT scrape full article bodies from news websites.
- Rationale: Respect robots.txt and terms of service
- Verification: Code review for scraping logic

**REQ-018**: The system SHALL NOT store API keys in code or configuration files.
- Rationale: Security best practice
- Verification: Secret scanning tests

**REQ-019**: The system SHALL NOT modify input data files.
- Rationale: Preserve data provenance
- Verification: Immutable input pattern tests

**REQ-020**: The system SHALL NOT expose sensitive errors to users without sanitization.
- Rationale: Information security
- Verification: Error handling tests

### 3.5 Optional Requirements (Nice-to-Have)

**REQ-021**: WHERE possible, the system SHALL support multiple news queries concurrently.
- Rationale: Improve data collection efficiency
- Priority: Medium

**REQ-022**: WHERE possible, the system SHALL cache ECOS API responses to reduce redundant calls.
- Rationale: API rate limit conservation
- Priority: Low

**REQ-023**: WHERE possible, the system SHALL support custom word lists for stance detection.
- Rationale: Flexibility for different languages/contexts
- Priority: Low

---

## 4. Specifications

### 4.1 Data Schemas

**news_raw**:
```
query: str
published_at: datetime
title: str
summary: str
google_url: str (unique)
```

**news_scored**:
```
query: str
published_at: datetime
title: str
summary: str
google_url: str (unique)
text: str (title + summary)
hawk_count: int
dove_count: int
stance_score: int (hawk_count - dove_count)
```

**news_daily**:
```
date: date (unique)
n_articles: int
stance_mean: float
stance_sum: int
```

**rate_series**:
```
date: date (unique)
value: float
unit: str
name: str
source: str
```

**events**:
```
date: date (unique)
prev_value: float
value: float
diff: float
event_type: str (raise|hold|cut)
```

**event_study_table**:
```
event_date: date
event_type: str
date: date
day_offset: int (relative to event)
stance_mean: float
n_articles: int
```

### 4.2 Pipeline Configuration Parameters

**months_back**: int (default=6)
- Defines historical data collection window
- Affects date_range calculation

**event_window_days**: int (default=14)
- Defines event study window (±N days)
- Affects event_study_table generation

**queries**: list[str]
- News search queries for RSS
- Example: ["한국은행 기준금리", "통화정책", "금리"]

**hawk_words**: list[str]
- Keywords indicating hawkish stance
- Example: ["인상", "긴축", "물가압력", "과열", "억제", "경계", "매파"]

**dove_words**: list[str]
- Keywords indicating dovish stance
- Example: ["인하", "완화", "둔화", "부양", "하방", "지원", "비둘기"]

**max_items_per_query**: int
- Limits RSS items per query
- Prevents excessive memory usage

### 4.3 Module Architecture

**src/ratestance/**
```
__init__.py
config.py          # Configuration management (pydantic BaseSettings)
collector/         # Data collection modules
  __init__.py
  news_collector.py    # RSS feed collection
  ecos_client.py       # ECOS API client
scorer/            # Text scoring modules
  __init__.py
  stance_scorer.py     # Hawkish/dovish scoring
aggregator/        # Data aggregation modules
  __init__.py
  daily_aggregator.py  # Daily aggregation
analyzer/          # Analysis modules
  __init__.py
  event_detector.py    # Rate change event detection
  event_study.py       # Event study analysis
visualizer/        # Visualization modules
  __init__.py
  plots.py             # Plot generation
pipeline.py        # Main pipeline orchestration
cli.py             # Command-line interface
tests/             # Test suite
  test_collector.py
  test_scorer.py
  test_aggregator.py
  test_analyzer.py
  test_pipeline.py
```

### 4.4 API Interfaces

**NewsCollector.collect()**:
```python
def collect(
    queries: list[str],
    start_date: date,
    end_date: date,
    max_items: int
) -> pd.DataFrame:
    """Collect news from RSS feeds.

    Returns:
        DataFrame with news_raw schema
    """
```

**EcosClient.fetch_base_rates()**:
```python
def fetch_base_rates(
    start_date: date,
    end_date: date,
    api_key: str
) -> pd.DataFrame:
    """Fetch base rate series from ECOS API.

    Returns:
        DataFrame with rate_series schema
    """
```

**StanceScorer.score()**:
```python
def score(
    articles: pd.DataFrame,
    hawk_words: list[str],
    dove_words: list[str]
) -> pd.DataFrame:
    """Score articles for hawkish/dovish stance.

    Returns:
        DataFrame with news_scored schema
    """
```

**EventDetector.detect_events()**:
```python
def detect_events(
    rate_series: pd.DataFrame
) -> pd.DataFrame:
    """Detect rate change events.

    Returns:
        DataFrame with events schema
    """
```

**EventStudy.analyze()**:
```python
def analyze(
    events: pd.DataFrame,
    daily_stance: pd.DataFrame,
    window_days: int
) -> pd.DataFrame:
    """Perform event study analysis.

    Returns:
        DataFrame with event_study_table schema
    """
```

---

## 5. Non-Goals (Explicit Exclusions)

### 5.1 Out of Scope

- **Large-scale article body scraping**: Violates robots.txt and terms of service
- **Deep learning sentiment analysis**: Explainability prioritized over accuracy
- **Real-time web service**: MVP is notebook/script-based, not production API
- **Multi-language support**: Korean news only for MVP
- **Historical data beyond ECOS coverage**: Manual data collection not automated
- **Predictive modeling**: Descriptive analysis only, no forecasting
- **User interface**: CLI-only, no web UI

### 5.2 Future Enhancements (Not in MVP)

- Real-time streaming news processing
- Machine learning-based stance classification
- Multi-central bank comparison
- Interactive dashboard
- API server for programmatic access
- Database persistence layer
- Advanced NLP (topic modeling, named entity recognition)

---

## 6. Deliverables

### 6.1 Data Files (data/)

- news_raw.csv
- news_scored.csv
- news_daily.csv
- rate_series.csv
- events.csv
- event_study_table.csv

### 6.2 Outputs (outputs/)

- news_stance_timeseries.png (Time series of daily stance scores)
- event_study.png (Event study visualization by event type)

### 6.3 Documentation

- README.md (Setup, usage, interpretation guide)
- API documentation (docstrings for all modules)
- CHANGELOG.md (Version history)

---

## 7. Success Metrics

### 7.1 Functional Requirements

- [ ] months_back parameter changes actual data collection period
- [ ] 100+ news articles collected from RSS feeds
- [ ] At least 1 base rate data point retrieved from ECOS
- [ ] Event table generated (hold-only acceptable if no changes)
- [ ] Event study plot generated (graceful handling if no events)

### 7.2 Quality Requirements

- [ ] Test coverage ≥ 85% (per quality.yaml constitution)
- [ ] Zero linter errors (ruff)
- [ ] Zero type errors (mypy)
- [ ] All tests passing (pytest)

### 7.3 TRUST 5 Compliance

**Tested**:
- Characterization tests for data collection
- Unit tests for scoring logic
- Integration tests for pipeline

**Readable**:
- Clear variable naming (English)
- Docstrings for all public functions
- Type hints for all functions

**Unified**:
- Black code formatting
- isort import organization
- Consistent structure

**Secured**:
- API keys via environment variables only
- Input validation for all parameters
- No secrets in code

**Trackable**:
- Git commits with Conventional Commits
- Clear file organization
- Comprehensive logging

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Risk**: ECOS_API_KEY missing or invalid
- **Impact**: Pipeline cannot collect rate data
- **Mitigation**: Early validation with clear error message
- **Fallback**: Use synthetic rate data for testing

**Risk**: RSS feed returns insufficient results
- **Impact**: Analysis based on sparse data
- **Mitigation**: Warning log, continue with available data
- **Fallback**: Expand query list or time window

**Risk**: ECOS API response structure changes
- **Impact**: Rate collection failures
- **Mitigation**: Defensive parsing with regex fallback
- **Fallback**: Manual data entry template

**Risk**: Network connectivity issues
- **Impact**: Data collection failures
- **Mitigation**: Retry logic with exponential backoff
- **Fallback**: Cached data from previous runs

### 8.2 Data Quality Risks

**Risk**: News articles lack stance indicators
- **Impact**: Low stance score variance
- **Mitigation**: Expand word lists, analyze keyword coverage
- **Fallback**: Manual annotation sample for validation

**Risk**: Duplicate articles in RSS feeds
- **Impact**: Biased stance scores
- **Mitigation**: Deduplication by google_url, then (title, date)
- **Fallback**: Manual duplicate detection review

**Risk**: Publication date inaccuracies
- **Impact**: Misaligned event study windows
- **Mitigation**: Date validation and outlier detection
- **Fallback**: Exclude articles with suspicious dates

---

## 9. Traceability

### 9.1 Requirement Mapping

| REQ ID | Module | Test Case |
|--------|--------|-----------|
| REQ-005 | pipeline.py | test_date_range_calculation |
| REQ-006 | news_collector.py | test_rss_collection |
| REQ-007 | stance_scorer.py | test_stance_scoring |
| REQ-008 | daily_aggregator.py | test_daily_aggregation |
| REQ-009 | ecos_client.py | test_ecos_fetch |
| REQ-010 | event_detector.py | test_event_detection |
| REQ-011 | event_study.py | test_event_study |
| REQ-012 | plots.py | test_visualization |

### 9.2 Acceptance Criteria Mapping

| AC ID | Requirement(s) | Verification Method |
|-------|----------------|---------------------|
| AC-001 | REQ-005 to REQ-012 | End-to-end pipeline test |
| AC-002 | REQ-013 | Environment variable test |
| AC-003 | REQ-014 | Sparse data handling test |
| AC-004 | REQ-015 | Hold-only event test |
| AC-005 | REQ-001 to REQ-004 | Integration tests |

---

## 10. References

### 10.1 External APIs

- ECOS Open API: https://ecos.bok.or.kr/api/
- Google News RSS: https://news.google.com/rss/search

### 10.2 Research Context

- Event Study Methodology: Standard finance research methodology
- Monetary Policy Communication: Central bank forward guidance literature
- Sentiment Analysis in Finance: Text as data for economic research

### 10.3 Technical Standards

- Python 3.11+ Documentation
- PEP 8 Style Guide
- Pydantic Documentation
- pandas Documentation
- pytest Documentation

---

**SPEC Status**: Completed
**Assigned To**: TBD

---

*This specification is written in EARS format and serves as the single source of truth for RateStance MVP implementation.*

<moai>COMPLETE</moai>
