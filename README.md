# RateStance

통화정책 뉴스 스탠스 분석 파이프라인 및 대시보드. 한국은행(BoK) 기준금리 결정과 금융 뉴스 감성(매파/비둘기파) 간의 관계를 자동으로 분석합니다.

## 개요

RateStance는 Google News RSS 및 GDELT BigQuery에서 경제 뉴스를 수집하고, ECOS OpenAPI를 통해 한국은행 기준금리를 조회한 후, 금리 변동 이벤트 전후의 뉴스 감성 변화를 분석하는 자동화된 데이터 파이프라인입니다.

## 핵심 기능

- **이중 소스 뉴스 수집**: GDELT BigQuery(과거 데이터)와 Google News RSS(현재 뉴스) 통합
- **자동 감성 분석**: 매파/비둘기파 키워드 기반 스탠스 스코어링
- **이벤트 스터디 분석**: 금리 변동 전후 ±14일 뉴스 논조 변화 추적
- **대시보드 시각화**: 실시간 뉴스 스탠스 시계열, 기준금리, 이벤트 분석 결과 표시
- **REST API**: 데이터 조회 및 비동기 갱신 엔드포인트

## 배포 정보

- **대시보드**: https://ip9202.site/economy (Next.js)
- **API**: https://ip9202.site/api/ (FastAPI, 포트 8001)
- **서버**: ip9202.site (PM2 프로세스 관리)

## Installation

### Prerequisites

- Python 3.11 or higher
- ECOS API key (get from https://ecos.bok.or.kr/api/)

### 설정

```bash
# 저장소 클론
git clone https://github.com/ip9202/economy_scrap.git
cd economy_scrap

# Python 3.11 사용 필수 (uv 사용 권장)
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 ECOS_API_KEY 추가
```

### 필수 요구사항

- Python 3.11+
- ECOS API 키: https://ecos.bok.or.kr/api/
- BigQuery 접근(선택): 과거 뉴스 데이터 수집 시

## 사용 방법

### 파이프라인 실행

```bash
# 기본값으로 실행 (6개월 데이터, ±14일 윈도우)
uv run python -m ratestance.cli

# 커스텀 파라미터
uv run python -m ratestance.cli --months-back 3 --event-window 7
```

### 대시보드 실행

```bash
# 백엔드 API 시작
uv run python -m ratestance.api

# 프론트엔드 개발 서버 (별도 터미널)
cd dashboard && npm run dev
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

## 개발

### 테스트 실행

```bash
# 모든 테스트 실행 (커버리지 포함)
uv run python -m pytest tests/ --cov=src/ratestance

# 특정 테스트 파일
uv run python -m pytest tests/test_news_collector.py -v
```

**현재 상태**: 50개 테스트, 93.24% 코드 커버리지 (목표: 85%+)

### 코드 품질

```bash
# Ruff 린팅
ruff check src/ tests/

# 타입 체크
mypy src/ratestance --strict

# 포매팅
black src/ tests/
```

## 프로젝트 구조

```
src/ratestance/
├── config.py              # 설정 관리 (Pydantic)
├── cli.py                 # CLI 진입점
├── pipeline.py            # 파이프라인 오케스트레이션
│
├── collector/             # 데이터 수집
│   ├── news_collector.py  # Google News RSS
│   ├── ecos_client.py     # 한국은행 ECOS API
│   └── gdelt_client.py    # GDELT BigQuery (과거 데이터)
│
├── scorer/                # 감성 분석
│   └── stance_scorer.py   # 키워드 기반 스탠스 스코어링
│
├── aggregator/            # 데이터 집계
│   └── daily_aggregator.py # 일별 집계
│
├── analyzer/              # 분석 모듈
│   ├── event_detector.py  # 금리 변동 감지
│   └── event_study.py     # 이벤트 스터디 분석
│
├── visualizer/            # 시각화
│   └── plots.py           # Matplotlib 차트
│
└── api/                   # FastAPI 애플리케이션
    ├── main.py            # 앱 초기화
    ├── routes.py          # API 엔드포인트
    ├── refresh_models.py  # Pydantic 모델
    └── job_store.py       # 비동기 Job 관리
```

## API 문서

주요 엔드포인트:

- `GET /api/data/news-daily`: 일별 뉴스 스탠스 집계
- `GET /api/data/rate-series`: 기준금리 시계열
- `GET /api/data/events`: 감지된 금리 변동 이벤트
- `GET /api/data/event-study`: 이벤트 스터디 분석 결과
- `GET /api/data/news-articles`: 개별 뉴스 기사 (페이지네이션)
- `POST /api/data/refresh`: 파이프라인 실행 (비동기 Job)

## 관련 문서

- [PRD.md](./PRD.md) - 상세 제품 요구사항 문서
- [SCRIPT.md](./SCRIPT.md) - 프로젝트 프레젠테이션 스크립트
- [CHANGELOG.md](./CHANGELOG.md) - 버전 변경 이력

## 라이선스

MIT License

## 감사의 말

- 한국은행 ECOS 공개 API
- Google News RSS 피드
- GDELT Project (BigQuery 데이터)
