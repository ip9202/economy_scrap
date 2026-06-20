# Changelog

All notable changes to RateStance MVP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-20

### Added
- **미국 금리 시각화**: FRED Federal Funds Rate 데이터를 금리 시계열 차트에 한국 기준금리와 함께 표시
  - `GET /api/data/us-rate-series` 엔드포인트 추가
  - 차트에 Legend 추가 (한국/미국 구분)
  - FRED 월별 데이터를 한국 일별 데이터에 forward-fill 매핑
- **최근 금리 결정 비교 카드 (RateEventCard)**: 최근 금리 결정과 직전 결정을 인상/인하/동결 아이콘 및 %p 변동폭으로 시각화
  - 인상: 빨간색 상승 화살표 / 인하: 파란색 하강 화살표 / 동결: 회색 수평선
  - 최근 결정 날짜·금리·변동폭 + 직전 결정 요약 표시
  - `GET /api/data/statistics` 응답에 `latest_event_detail`, `prev_event_detail` 필드 추가
- **다음 발표일 배너 (NextMeetingBanner)**: 한국은행(BOK) 및 FOMC 다음 금리 결정 예정일을 D-day 형식으로 표시
  - `GET /api/data/next-meetings` 엔드포인트 추가
- **이벤트 스터디 차트 개선**: 데이터 포인트에 dot 마커 추가로 희소 데이터 가시성 향상

### Fixed
- **이벤트 스터디 분석 데이터 미표시**: API 날짜 필터가 2021~2025년 이벤트를 모두 제외하는 문제 수정
  - 이벤트 스터디는 역사적 분석이므로 날짜 범위 필터 제거
  - `useEventStudy` 훅에서 날짜 범위 의존성 제거 (항상 전체 데이터 fetch)
- **미국 금리 차트 미표시**: FRED 월초 날짜(`YYYY-MM-01`)가 날짜 범위 필터에 제외되는 문제 수정
  - `useUsRateSeries` 훅에서 날짜 범위 의존성 제거 (전체 시계열 항상 fetch)
- **뉴스 툴팁 기사수 불일치**: 날짜 클릭 후 표시 기사수가 툴팁과 다른 문제 수정
- **날짜 클릭 시 뉴스 없음**: API에서 `days=0` 파라미터 처리 오류 수정
- **FRED 날짜 필터링**: 월별 US 금리 날짜를 월 단위(`YYYY-MM`)로 비교하도록 수정
- **최근 이벤트 통계**: 이벤트 통계에서 실제 금리 변동 이벤트만 집계하도록 수정 (hold 제외)

### Changed
- `GET /api/data/statistics` 응답 구조 확장 (하위 호환 유지)
- 금리 시계열 차트에 한국/미국 금리 Legend 표시 추가

## [0.1.1] - 2026-03-11

### Fixed
- 프로덕션 대시보드 API 연결 오류 수정 (localhost:8000 → 상대 경로)
  - `.env.local`의 `NEXT_PUBLIC_API_URL`이 빌드에 포함되어 프로덕션에서 API 호출 실패
  - `.env.development`로 로컬 개발 설정 분리, 프로덕션은 nginx 프록시 사용

## [0.1.0] - 2026-03-10

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
