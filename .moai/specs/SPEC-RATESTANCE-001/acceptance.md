# RateStance MVP - Acceptance Criteria

## TAG BLOCK

```
TAG: SPEC-RATESTANCE-001
PROJECT: RateStance MVP
PHASE: Plan
DOCUMENT: acceptance.md
STATUS: Ready for Implementation
CREATED: 2026-01-27
```

---

## 1. Definition of Done

A feature is considered complete when:

- [ ] All requirements implemented per SPEC (spec.md)
- [ ] All acceptance criteria met (this document)
- [ ] Test coverage ≥ 85%
- [ ] Zero ruff linter errors
- [ ] Zero mypy type errors
- [ ] All tests passing (pytest)
- [ ] Documentation complete (README, docstrings)
- [ ] Code reviewed and approved

---

## 2. Acceptance Criteria (Given-When-Then Format)

### AC-001: Complete Pipeline Execution

**Story**: As a researcher, I want to run the full pipeline to get analysis results

**Given**:
- ECOS_API_KEY environment variable is set
- Internet connectivity is available
- Default configuration is used

**When**:
- I execute `python -m ratestance.cli` from command line
- Or I run `Pipeline(Settings()).run()` from Python

**Then**:
- Pipeline executes all 8 stages without errors
- 6 CSV files are created in data/ directory:
  - news_raw.csv
  - news_scored.csv
  - news_daily.csv
  - rate_series.csv
  - events.csv
  - event_study_table.csv
- 2 PNG files are created in outputs/ directory:
  - news_stance_timeseries.png
  - event_study.png
- Log file is created in logs/ directory with timestamps
- Success message is displayed to user

**Verification**:
```bash
# Run pipeline
python -m ratestance.cli --months-back 6 --event-window 14

# Check outputs
ls -la data/
ls -la outputs/
ls -la logs/

# Verify file existence
test -f data/news_raw.csv
test -f data/news_scored.csv
test -f data/news_daily.csv
test -f data/rate_series.csv
test -f data/events.csv
test -f data/event_study_table.csv
test -f outputs/news_stance_timeseries.png
test -f outputs/event_study.png
```

---

### AC-002: Configuration Parameter Validation

**Story**: As a user, I want to customize pipeline parameters

**Given**:
- Project is installed
- Environment is configured

**When**:
- I provide `--months-back 3` flag
- Or I provide `--event-window 7` flag
- Or I modify queries list in .env file

**Then**:
- Date range calculation respects months_back parameter
- Event study window respects event_window_days parameter
- RSS queries use custom query list
- Configuration is validated before pipeline execution
- Invalid parameters raise clear error messages

**Verification**:
```python
# Test months_back parameter
config = Settings(months_back=3)
pipeline = Pipeline(config)
date_range = pipeline._calculate_date_range()
assert (date_range.end - date_range.start).days == approx(90)

# Test event_window_days parameter
config = Settings(event_window_days=7)
pipeline = Pipeline(config)
results = pipeline.run()
event_study = results["event_study_table"]
assert event_study["day_offset"].min() == -7
assert event_study["day_offset"].max() == 7
```

---

### AC-003: News Collection and Deduplication

**Story**: As a researcher, I want to collect unique news articles

**Given**:
- RSS feeds are accessible
- Date range is specified
- Queries list is configured

**When**:
- Pipeline collects news from RSS feeds
- Multiple queries return overlapping articles
- Some articles have identical URLs

**Then**:
- news_raw.csv contains unique articles only
- Deduplication is performed by google_url first
- Secondary deduplication by (title, published_at) tuple
- Article count reflects deduplication
- All articles are within specified date range
- Each article has required fields: query, published_at, title, summary, google_url

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/news_raw.csv")

# Check required columns
required_cols = ["query", "published_at", "title", "summary", "google_url"]
assert all(col in df.columns for col in required_cols)

# Check deduplication
assert df["google_url"].is_unique

# Check date range
df["published_at"] = pd.to_datetime(df["published_at"])
assert df["published_at"].min() >= start_date
assert df["published_at"].max() <= end_date

# Check minimum article count
assert len(df) >= 100
```

---

### AC-004: Stance Scoring Accuracy

**Story**: As a researcher, I want accurate stance scores

**Given**:
- news_raw.csv contains articles
- Hawk and dove word lists are configured

**When**:
- Pipeline scores articles for stance
- Article contains hawkish keywords
- Article contains dovish keywords
- Article contains both types

**Then**:
- news_scored.csv contains hawk_count, dove_count, stance_score
- stance_score = hawk_count - dove_count
- Positive score indicates hawkish stance
- Negative score indicates dovish stance
- Zero score indicates neutral/no stance
- Keyword counting is case-insensitive
- Text includes title + summary

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/news_scored.csv")

# Check columns
required_cols = ["hawk_count", "dove_count", "stance_score"]
assert all(col in df.columns for col in required_cols)

# Check formula
assert all(df["stance_score"] == df["hawk_count"] - df["dove_count"])

# Check case-insensitivity
hawk_sample = df[df["text"].str.contains("인상", case=False)]
assert hawk_sample["hawk_count"].sum() > 0

# Check variance
assert df["stance_score"].std() > 0  # Some variance exists
```

---

### AC-005: Daily Aggregation

**Story**: As a researcher, I want daily aggregated stance metrics

**Given**:
- news_scored.csv contains scored articles
- Multiple articles exist per day

**When**:
- Pipeline aggregates to daily level
- Day has 5 articles with scores [-2, -1, 0, 1, 2]

**Then**:
- news_daily.csv contains one row per day
- Columns: date, n_articles, stance_mean, stance_sum
- stance_mean = mean(stance_score) for that day
- stance_sum = sum(stance_score) for that day
- n_articles = count of articles for that day
- Date range covers all articles
- No gaps in consecutive dates (NaN allowed for no articles)

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/news_daily.csv")

# Check columns
required_cols = ["date", "n_articles", "stance_mean", "stance_sum"]
assert all(col in df.columns for col in required_cols)

# Check aggregation logic
sample_day = df.iloc[0]
# Verify: stance_mean * n_articles ≈ stance_sum
assert abs(sample_day["stance_mean"] * sample_day["n_articles"] - sample_day["stance_sum"]) < 0.01

# Check date coverage
df["date"] = pd.to_datetime(df["date"])
assert (df["date"].max() - df["date"].min()).days >= 30 * 6  # 6 months
```

---

### AC-006: ECOS Rate Collection

**Story**: As a researcher, I want official base rate data

**Given**:
- ECOS_API_KEY is set
- Date range is specified
- ECOS API is accessible

**When**:
- Pipeline requests rate data from ECOS
- API returns JSON response
- Response contains "한국은행 기준금리" statistic

**Then**:
- rate_series.csv contains time series data
- Columns: date, value, unit, name, source
- At least 1 data point is retrieved
- Dates are within requested range
- Values are numeric (float)
- Defensive parsing handles malformed responses
- API errors are retried with exponential backoff

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/rate_series.csv")

# Check columns
required_cols = ["date", "value", "unit", "name", "source"]
assert all(col in df.columns for col in required_cols)

# Check data existence
assert len(df) >= 1

# Check data types
df["value"] = pd.to_numeric(df["value"], errors="raise")
assert df["value"].notna().all()

# Check date range
df["date"] = pd.to_datetime(df["date"])
assert df["date"].min() >= start_date
assert df["date"].max() <= end_date

# Check metadata
assert "한국은행 기준금리" in df["name"].iloc[0]
assert df["source"].iloc[0] == "ECOS"
```

---

### AC-007: Event Detection

**Story**: As a researcher, I want to detect rate change events

**Given**:
- rate_series.csv contains time series
- Rates change at some dates
- Rates stay same at other dates

**When**:
- Pipeline detects events from rate series
- Rate increases from 3.50 to 3.75
- Rate decreases from 3.75 to 3.50
- Rate stays at 3.50

**Then**:
- events.csv contains all rate dates
- Columns: date, prev_value, value, diff, event_type
- diff > 0 → event_type = "raise"
- diff < 0 → event_type = "cut"
- diff == 0 → event_type = "hold"
- All rate changes are captured
- Hold events include unchanged rates

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/events.csv")

# Check columns
required_cols = ["date", "prev_value", "value", "diff", "event_type"]
assert all(col in df.columns for col in required_cols)

# Check event types
assert set(df["event_type"].unique()).issubset({"raise", "hold", "cut"})

# Check logic
raises = df[df["event_type"] == "raise"]
assert all(raises["diff"] > 0)

cuts = df[df["event_type"] == "cut"]
assert all(cuts["diff"] < 0)

holds = df[df["event_type"] == "hold"]
assert all(holds["diff"] == 0)

# Check diff calculation
assert all(df["diff"] == df["value"] - df["prev_value"])
```

---

### AC-008: Event Study Analysis

**Story**: As a researcher, I want to analyze tone around events

**Given**:
- events.csv contains rate events
- news_daily.csv contains daily stance
- event_window_days = 14

**When**:
- Pipeline performs event study
- Event occurs on 2026-01-15
- News data exists from 2026-01-01 to 2026-01-30

**Then**:
- event_study_table.csv contains window data
- Columns: event_date, event_type, date, day_offset, stance_mean, n_articles
- day_offset ranges from -14 to +14
- Each event has 29 rows (window * 2 + 1)
- stance_mean is aggregated per day per event
- Events with no news in window have NaN stance_mean

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/event_study_table.csv")

# Check columns
required_cols = ["event_date", "event_type", "date", "day_offset", "stance_mean", "n_articles"]
assert all(col in df.columns for col in required_cols)

# Check window range
assert df["day_offset"].min() == -14
assert df["day_offset"].max() == 14

# Check rows per event
event_counts = df.groupby("event_date").size()
assert all(event_counts == 29)  # 14 * 2 + 1

# Check day offset logic
sample_event = df[df["event_date"] == df["event_date"].iloc[0]]
assert sample_event[sample_event["day_offset"] == 0]["date"].iloc[0] == sample_event["event_date"].iloc[0]
```

---

### AC-009: Visualization Generation

**Story**: As a researcher, I want visual plots for analysis

**Given**:
- Pipeline completed successfully
- Output files exist

**When**:
- I open outputs/news_stance_timeseries.png
- I open outputs/event_study.png

**Then**:
**news_stance_timeseries.png**:
- X-axis shows date range
- Y-axis shows stance_mean
- Line plot connects daily points
- Vertical lines mark rate change events
- Legend indicates event types
- Title and axis labels are clear

**event_study.png**:
- X-axis shows day_offset (-14 to +14)
- Y-axis shows stance_mean
- Separate facet or line for each event_type
- Error bars or confidence intervals shown
- Vertical line at day_offset = 0
- Title and axis labels are clear

**Verification**:
```bash
# Check file existence
test -f outputs/news_stance_timeseries.png
test -f outputs/event_study.png

# Check file size (non-zero)
test -s outputs/news_stance_timeseries.png
test -s outputs/event_study.png

# Visual inspection (manual)
open outputs/news_stance_timeseries.png
open outputs/event_study.png
```

---

### AC-010: Error Handling - Missing API Key

**Story**: As a user, I want clear error when API key is missing

**Given**:
- Project is installed
- ECOS_API_KEY environment variable is not set

**When**:
- I execute `python -m ratestance.cli`

**Then**:
- Pipeline terminates immediately
- Error message is displayed: "ECOS_API_KEY environment variable is required"
- No partial output files are created
- Exit code is non-zero (1)
- Log file contains error details

**Verification**:
```bash
# Unset API key
unset ECOS_API_KEY

# Run pipeline
python -m ratestance.cli

# Check exit code
echo $?
assert $? == 1

# Check no partial outputs
assert ! test -f data/news_raw.csv
```

---

### AC-011: Error Handling - Sparse RSS Results

**Story**: As a user, I want pipeline to continue with sparse data

**Given**:
- RSS feeds return < 10 articles
- Date range is specified

**When**:
- Pipeline collects news from RSS

**Then**:
- Warning is logged: "Low article count detected: N articles"
- Pipeline continues execution
- Analysis uses available data
- Results may have higher variance
- No crash occurs

**Verification**:
```python
# Mock sparse RSS response
# Run pipeline with mock
# Verify warning in logs
# Verify pipeline completes
```

---

### AC-012: Error Handling - No Rate Changes

**Story**: As a user, I want analysis even when rates unchanged

**Given**:
- Rate series contains no changes (all hold events)
- Date range is specified

**When**:
- Pipeline detects events and performs event study

**Then**:
- events.csv contains only hold events
- event_study_table.csv is generated with hold events only
- Plot shows hold event analysis
- Warning is logged: "No raise/cut events detected, analyzing hold events only"
- Pipeline completes successfully

**Verification**:
```python
import pandas as pd

df = pd.read_csv("data/events.csv")

# Check only hold events
assert set(df["event_type"].unique()) == {"hold"}

# Check event study generated
df_study = pd.read_csv("data/event_study_table.csv")
assert len(df_study) > 0
```

---

### AC-013: Code Quality - Test Coverage

**Story**: As a developer, I want high test coverage

**Given**:
- All modules are implemented
- Tests are written

**When**:
- I run `pytest --cov src/ratestance`

**Then**:
- Test coverage report is generated
- Overall coverage ≥ 85%
- Coverage by module:
  - collector: ≥ 90%
  - scorer: ≥ 95%
  - aggregator: ≥ 90%
  - analyzer: ≥ 90%
  - visualizer: ≥ 80%
  - pipeline: ≥ 85%
- HTML coverage report is generated

**Verification**:
```bash
pytest --cov=src/ratestance --cov-report=html --cov-report=term-missing

# Check output
# Name                      Stmts   Miss  Cover   Missing
# --------------------------------------------------------
# ratestance/collector        50      5    90%   23-27
# ratestance/scorer           30      1    95%   45
# ...
# --------------------------------------------------------
# TOTAL                      200     25    87%
```

---

### AC-014: Code Quality - Linting and Type Checking

**Story**: As a developer, I want clean code

**Given**:
- All modules are implemented

**When**:
- I run `ruff check src/ tests/`
- I run `mypy src/ratestance --strict`

**Then**:
- Zero ruff errors
- Zero ruff warnings
- Zero mypy errors
- All code is formatted with black
- All imports are sorted with isort

**Verification**:
```bash
# Linting
ruff check src/ tests/
# Expected: No errors found

# Type checking
mypy src/ratestance --strict
# Expected: Success: no issues found in 10 source files

# Formatting
black --check src/ tests/
# Expected: No reformatting needed
```

---

### AC-015: Documentation Quality

**Story**: As a new user, I want to understand and use the pipeline

**Given**:
- Project is cloned or installed

**When**:
- I read README.md
- I follow installation instructions
- I run example pipeline command

**Then**:
- README contains:
  - Project overview
  - Installation instructions
  - ECOS API key acquisition guide
  - Usage examples
  - Output file descriptions
  - Interpretation guide for stance scores
- All public functions have Google-style docstrings
- Type hints are present for all function parameters
- Example code in docstrings is runnable

**Verification**:
```bash
# Check README exists
test -f README.md

# Check README sections
grep -q "## Installation" README.md
grep -q "## Usage" README.md
grep -q "## Outputs" README.md

# Check docstrings
python -c "import ratestance; help(ratestance.Pipeline.run)"
# Expected: Detailed docstring with parameters and returns
```

---

## 3. Quality Gates

### 3.1 TRUST 5 Validation

**Tested**:
- [ ] Characterization tests for data collectors
- [ ] Unit tests for core logic (scoring, aggregation)
- [ ] Integration tests for pipeline stages
- [ ] Edge case tests (empty data, missing fields)
- [ ] Coverage ≥ 85%

**Readable**:
- [ ] Clear variable names (English, descriptive)
- [ ] Google-style docstrings
- [ ] Type hints for all functions
- [ ] Code comments explain complex logic
- [ ] Module-level documentation

**Unified**:
- [ ] Black code formatting applied
- [ ] isort import organization
- [ ] Consistent naming conventions
- [ ] Uniform error handling patterns
- [ ] Consistent logging format

**Secured**:
- [ ] API keys via environment variables only
- [ ] Input validation for all parameters
- [ ] No secrets in code or git history
- [ ] Safe URL handling (no injection)
- [ ] File path validation

**Trackable**:
- [ ] Conventional Commits for git
- [ ] Clear module organization
- [ ] Comprehensive logging
- [ ] Progress indicators in CLI
- [ ] Version tags for releases

### 3.2 Automated Checks

**Pre-Commit Hooks**:
```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

ruff check src/ tests/
mypy src/ratestance --strict
pytest --cov --cov-fail-under=85
black --check src/ tests/
```

**CI/CD Pipeline**:
- Run on every push and pull request
- Execute all quality checks
- Fail build if any check fails
- Report coverage to Codecov

---

## 4. Test Scenarios

### 4.1 Happy Path Tests

**Test Case 1: Full Pipeline with Default Config**
```python
def test_full_pipeline_default_config():
    """Test pipeline execution with default configuration."""
    config = Settings()
    pipeline = Pipeline(config)
    results = pipeline.run()

    assert "news_raw" in results
    assert "news_scored" in results
    assert "news_daily" in results
    assert "rate_series" in results
    assert "events" in results
    assert "event_study_table" in results

    assert len(results["news_raw"]) >= 100
    assert len(results["events"]) >= 1
```

**Test Case 2: Pipeline with Custom Parameters**
```python
def test_pipeline_custom_parameters():
    """Test pipeline with custom months_back and event_window."""
    config = Settings(months_back=3, event_window_days=7)
    pipeline = Pipeline(config)
    results = pipeline.run()

    # Verify date range
    news_raw = results["news_raw"]
    date_range = news_raw["published_at"].max() - news_raw["published_at"].min()
    assert date_range.days <= 92  # 3 months + buffer

    # Verify event window
    event_study = results["event_study_table"]
    assert event_study["day_offset"].min() == -7
    assert event_study["day_offset"].max() == 7
```

### 4.2 Edge Case Tests

**Test Case 3: Empty RSS Feed**
```python
def test_empty_rss_feed():
    """Test pipeline behavior when RSS returns no articles."""
    # Mock empty RSS response
    with mock("feedparser.parse", return_value={"entries": []}):
        pipeline = Pipeline(Settings())
        with pytest.raises(ValueError, match="No articles collected"):
            pipeline.run()
```

**Test Case 4: Missing ECOS API Key**
```python
def test_missing_ecos_api_key():
    """Test pipeline behavior without API key."""
    with mock.dict(os.environ, {"ECOS_API_KEY": ""}):
        with pytest.raises(ValueError, match="ECOS_API_KEY required"):
            config = Settings()
            pipeline = Pipeline(config)
            pipeline.run()
```

**Test Case 5: No Rate Changes**
```python
def test_no_rate_changes():
    """Test event detection with constant rate series."""
    rate_series = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=10),
        "value": [3.5] * 10
    })

    detector = EventDetector()
    events = detector.detect(rate_series)

    assert all(events["event_type"] == "hold")
    assert len(events) == 10
```

### 4.3 Integration Tests

**Test Case 6: End-to-End with Fixture Data**
```python
def test_end_to_end_with_fixture_data():
    """Test full pipeline with fixture data."""
    # Load fixture data
    news_fixture = pd.read_csv("tests/fixtures/sample_news.csv")
    rates_fixture = pd.read_csv("tests/fixtures/sample_rates.csv")

    # Mock collectors
    with mock("ratestance.collector.NewsCollector.collect", return_value=news_fixture):
        with mock("ratestance.collector.EcosClient.fetch_base_rates", return_value=rates_fixture):
            pipeline = Pipeline(Settings())
            results = pipeline.run()

    # Verify all outputs
    assert results["news_raw"].equals(news_fixture)
    assert results["rate_series"].equals(rates_fixture)
    assert len(results["events"]) > 0
    assert len(results["event_study_table"]) > 0
```

---

## 5. Manual Verification Checklist

### 5.1 Setup Verification

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (poetry install or pip install -r requirements.txt)
- [ ] ECOS_API_KEY acquired and set in .env
- [ ] Tests passing (pytest)
- [ ] Linting passing (ruff check, mypy)

### 5.2 Functional Verification

- [ ] Pipeline runs without errors
- [ ] All output files created
- [ ] Output files have correct schemas
- [ ] Plots are generated and viewable
- [ ] CLI arguments work as expected
- [ ] Logs show progress through stages

### 5.3 Data Quality Verification

- [ ] News articles collected (> 100)
- [ ] Deduplication working (no duplicate URLs)
- [ ] Stance scores vary (not all zero)
- [ ] Rate data retrieved (≥ 1 point)
- [ ] Events detected (raise/hold/cut)
- [ ] Event study has data in windows

### 5.4 Documentation Verification

- [ ] README is clear and comprehensive
- [ ] Installation instructions work
- [ ] Usage examples are accurate
- [ ] Docstrings present for all public functions
- [ ] Type hints present for all parameters

---

## 6. Sign-Off

### 6.1 Developer Sign-Off

**Developer**: ___________________
**Date**: ___________________
**Comments**: ___________________

### 6.2 Reviewer Sign-Off

**Reviewer**: ___________________
**Date**: ___________________
**Comments**: ___________________

### 6.3 Approval Criteria

- [ ] All acceptance criteria met
- [ ] All quality gates passed
- [ ] Documentation complete
- [ ] Code reviewed and approved
- [ ] Ready for sync phase

---

**Acceptance Status**: Ready for Validation
**Next Phase**: /moai:2-run SPEC-RATESTANCE-001
**Validation Method**: Automated tests + Manual verification

---

*This acceptance criteria document follows Given-When-Then format and ensures all requirements are verifiable.*
