# SPEC-UI-001: RateStance 데이터 대시보드 UI/UX

## TAG BLOCK

```yaml
spec_id: SPEC-UI-001
title: RateStance 데이터 대시보드 UI/UX 구현
status: Planned
priority: High
assigned: Alfred
created: 2026-01-27
lifecycle_level: spec-first
domain: UI
tags: [frontend, dashboard, visualization, stitch-mcp, react]
```

## Environment

### 시스템 환경

- **백엔드**: Python 3.14, FastAPI-style 구조 (src/ratestance/)
- **데이터 처리**: pandas, loguru, requests
- **시각화**: matplotlib (정적 PNG 생성 중)
- **데이터 위치**: data/*.csv (news_raw.csv, news_scored.csv, news_daily.csv, rate_series.csv, events.csv, event_study_table.csv)
- **시각화 출력**: outputs/*.png (news_stance_timeseries.png, event_study.png)

### 기술 제약사항

- [HARD] 백엔드 파이프라인 수정 최소화 (기존 Python 코드 유지)
- [HARD] 정적 PNG 파일 동적 시각화로 변환
- [HARD] 한국어 폰트 지원 (AppleGothic, Malgun Gothic)
- [SOFT] 반응형 디자인 (모바일/태블릿 지원)

### 도구

- **Stitch MCP**: UI/UX 디자인 생성
- **프론트엔드 프레임워크**: 미선택 (React/Vue/Next.js 후보)
- **차트 라이브러리**: Recharts, Chart.js, Plotly 후보

## Assumptions

### 기본 가정

1. **데이터 가용성**: 백엔드 파이프라인이 정상 실행되어 최신 CSV 파일이 data/ 디렉토리에 존재함
2. **API 서비스**: 백엔드에서 CSV 데이터를 제공하는 REST API 엔드포인트가 구현됨
3. **실시간 업데이트**: 사용자가 "새로고침" 버튼으로 최신 데이터를 불러올 수 있음
4. **단일 사용자**: 개인용 분석 도구로, 다중 사용자 인증은 불필요

### 검증 가정

- **데이터 볼륨**: 6개월 치 데이터 (약 180일 × 뉴스 기사 수)
- **응답 시간**: 차트 렌더링 3초 이내
- **브라우저 지원**: 최신 Chrome, Safari, Firefox (최신 2버전)

## Requirements (EARS Format)

### 1. 시스템 전체 요구사항 (Ubiquitous)

**REQ-1**: 시스템은 항상 모든 차트에서 한국어 텍스트를 올바르게 렌더링해야 한다.

**REQ-2**: 시스템은 항상 모든 데이터 시각화에서 일관된 색상 팔레트를 사용해야 한다.

**REQ-3**: 시스템은 항상 로딩 상태를 사용자에게 피드백으로 제공해야 한다.

### 2. 이벤트 기반 요구사항 (Event-Driven)

**REQ-4**: WHEN 사용자가 대시보드 페이지에 접근하면, 시스템은 SHALL 최신 뉴스 감성 시계열 차트를 렌더링한다.

**REQ-5**: WHEN 사용자가 금리 시계열 차트의 데이터 포인트를 호버하면, 시스템은 SHALL 해당 날짜의 금리 값과 뉴스 기사 수를 툴팁으로 표시한다.

**REQ-6**: WHEN 사용자가 이벤트 스터디 차트에서 특정 이벤트를 선택하면, 시스템은 SHALL 해당 이벤트 상세 정보를 사이드 패널에 표시한다.

**REQ-7**: WHEN 사용자가 "데이터 새로고침" 버튼을 클릭하면, 시스템은 SHALL 백엔드 API에서 최신 CSV 데이터를 가져와 차트를 업데이트한다.

**REQ-8**: WHEN 데이터 로딩이 실패하면, 시스템은 SHALL 사용자에게 명확한 에러 메시지를 표시하고 재시도 옵션을 제공한다.

### 3. 상태 기반 요구사항 (State-Driven)

**REQ-9**: IF 데이터가 존재하지 않는 날짜 범위가 있으면, 시스템은 SHALL 차트에서 해당 구간을 "데이터 없음"으로 시각적으로 구분한다.

**REQ-10**: IF 뉴스 감성 점수가 양수(매파)이면, 시스템은 SHALL 차트에서 빨간색 계열로 표시한다.

**REQ-11**: IF 뉴스 감성 점수가 음수(비둘기)이면, 시스템은 SHALL 차트에서 파란색 계열로 표시한다.

**REQ-12**: IF 브라우저 창 너비가 768px 미만이면, 시스템은 SHALL 모바일 최적화 레이아웃으로 전환한다.

### 4. 바람직한 요구사항 (Optional)

**REQ-13**: WHERE 가능하면, 시스템은 SHALL 차트 데이터를 CSV로 내보내는 기능을 제공한다.

**REQ-14**: WHERE 가능하면, 시스템은 SHALL 특정 날짜 범위를 선택하여 필터링하는 기능을 제공한다.

**REQ-15**: WHERE 가능하면, 시스템은 SHALL 뉴스 기사 제목을 클릭하여 원본 기사로 이동하는 링크를 제공한다.

### 5. 원치 않는 행동 요구사항 (Unwanted)

**REQ-16**: 시스템은 SHALL 페이지 리로드 없이 차트 간 전환 시 깜빡임(flash)이 발생하지 않아야 한다.

**REQ-17**: 시스템은 SHALL 데이터 로딩 중 UI가 응답하지 않는 상태(freeze)가 되지 않아야 한다.

**REQ-18**: 시스템은 SHALL 사용자가 상호작용하지 않은 차트에서 불필요한 애니메이션을 실행하지 않아야 한다.

## Specifications

### SP-1: 대시보드 레이아웃

**목적**: 사용자에게 4개 주요 시각화를 한눈에 제공

**구성요소**:

1. **헤더 섹션**
   - 프로젝트 타이틀: "RateStance: 금융 뉴스 감성 분석"
   - 마지막 업데이트 시간 표시
   - "데이터 새로고침" 버튼

2. **메인 차트 영역** (상단)
   - **뉴스 감성 시계열 차트** (좌측 70%)
     - X축: 날짜 (최근 6개월)
     - Y축: 일 평균 감성 점수 (-1.0 ~ +1.0)
     - 선 차트: 일별 평균 감성 점수
     - 색상: 양수(빨강), 음수(파랑)
     - 금리 변화 이벤트 마커 (수직 점선)

   - **금리 시계열 차트** (우측 30%)
     - X축: 날짜 (뉴스 차트와 동일)
     - Y축: 기준금리 (%)
     - 영역 차트(Area Chart)
     - 금리 인상/인하 이벤트 강조

3. **이벤트 스터디 영역** (중단)
   - **이벤트 스터디 차트**
     - X축: 이벤트 전후 일수 (-14일 ~ +14일)
     - Y축: 평균 감성 점수
     - 이벤트 유형별 색상 구분 (인상, 인하, 유지)
     - 신뢰 구간 표시 (95% CI)

4. **통계 요약 영역** (하단)
   - **키 메트릭 카드** (4개)
     - 총 뉴스 기사 수
     - 평균 감성 점수
     - 금리 변화 횟수
     - 가장 최근 이벤트

5. **뉴스 기사 리스트** (하단)
   - 일별 뉴스 기사 목록 (페이지네이션)
   - 기사 제목, 감성 점수, 날짜 표시
   - 클릭 시 원본 기사 링크 이동

### SP-2: API 엔드포인트 설계

**목적**: 프론트엔드에서 데이터를 가져오기 위한 REST API

**엔드포인트**:

```
GET /api/data/news-daily
- Response: { date: string, stance_mean: number, n_articles: number }[]
- Description: 일별 뉴스 감성 데이터

GET /api/data/rate-series
- Response: { date: string, value: number, unit: string }[]
- Description: 금리 시계열 데이터

GET /api/data/events
- Response: { date: string, event_type: string, description: string }[]
- Description: 금리 변화 이벤트 목록

GET /api/data/event-study
- Response: { event_date: string, event_type: string, day_offset: number, stance_mean: number }[]
- Description: 이벤트 스터디 분석 데이터

GET /api/data/statistics
- Response: { total_articles: number, avg_stance: number, event_count: number, latest_event: string }
- Description: 요약 통계
```

### SP-3: 기술 스택 결정

**프론트엔드 프레임워크**: **Next.js 16** (React 19)
- 이유: App Router, Server Components, SEO 최적화
- TypeScript: 타입 안정성
- Tailwind CSS: rapid styling

**차트 라이브러리**: **Recharts** (React 차트 라이브러리)
- 이유: React 친화적, 선언적 API, 커스터마이징 용이
- 대안: Chart.js, Plotly (복잡한 인터랙션 필요 시)

**UI 컴포넌트**: **shadcn/ui**
- 이유: 접근성, 모던 디자인, TypeScript 지원
- Radix UI primitives 기반

**데이터 페칭**: **TanStack Query (React Query)**
- 이유: 캐싱, 자동 리페칭, 에러 핸들링

### SP-4: Stitch MCP 활용

**UI/UX 디자인 생성**:

1. **Stitch로 생성할 컴포넌트**:
   - 대시보드 레이아웃 (Grid/Flex)
   - 차트 컴포넌트 스타일링
   - 카드 UI (통계 요약)
   - 데이터 테이블 (뉴스 기사 리스트)
   - 버튼 및 인터랙션 요소

2. **디자인 원칙**:
   - **색상**: Dark/Light 모드 지원
     - Primary: Indigo (#6366f1)
     - Success: Emerald (긍정적 감성)
     - Warning: Amber (중립적 감성)
     - Danger: Rose (부정적 감성)
   - **타이포그래피**: Pretendard (한국어 최적화)
   - **간격**: 4px grid system
   - **둥근 모서리**: 8px (카드), 4px (버튼)

3. **반응형 브레이크포인트**:
   - Mobile: < 640px
   - Tablet: 640px - 1024px
   - Desktop: > 1024px

## Traceability

| REQ ID | Specification | Test Scenario |
|--------|---------------|---------------|
| REQ-1 | SP-1: Korean font support | TS-1: Korean text rendering |
| REQ-4 | SP-1: Main chart rendering | TS-2: Dashboard initial load |
| REQ-5 | SP-1: Tooltip interaction | TS-3: Hover tooltip display |
| REQ-6 | SP-1: Event detail panel | TS-4: Event selection interaction |
| REQ-7 | SP-2: API refresh endpoint | TS-5: Data refresh functionality |
| REQ-10, REQ-11 | SP-1: Color scheme | TS-6: Stance color coding |
| REQ-12 | SP-4: Responsive breakpoints | TS-7: Mobile layout adaptation |
| REQ-16 | SP-3: Next.js routing | TS-8: Smooth page transitions |
| REQ-17 | SP-3: TanStack Query | TS-9: Loading state management |
