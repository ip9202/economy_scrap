# SPEC-UI-001: 구현 계획

## TAG BLOCK

```yaml
spec_id: SPEC-UI-001
related_specs: []
parent_epic: RateStance Dashboard
milestone: MVP Release
assigned: Alfred
status: Planned
priority: High
tags: [frontend, dashboard, visualization, implementation-plan]
traceability:
  requirements: spec.md#requirements
  acceptance: acceptance.md
```

## Milestones (우선순위 기반)

### 1차 마일스톤: 프로젝트 설정 및 기본 인프라 (Priority: High)

**목표**: 개발 환경 구축 및 기본 라우팅

**작업 항목**:

1. **Next.js 16 프로젝트 초기화**
   - `npx create-next-app@latest` 실행
   - TypeScript, Tailwind CSS, ESLint 설정
   - App Router 구조 확인

2. **의존성 설치**
   - `npm install recharts` (차트 라이브러리)
   - `npm install @tanstack/react-query` (데이터 페칭)
   - `npm install date-fns` (날짜 처리)
   - `npm install @radix-ui/react-*` (shadcn/ui 기본)

3. **디렉토리 구조 생성**
   ```
   app/
   ├── layout.tsx           # 루트 레이아웃
   ├── page.tsx             # 대시보드 메인 페이지
   ├── globals.css          # 전역 스타일
   └── api/                 # API 라우트 (백엔드 연동)
   components/
   ├── dashboard/           # 대시보드 컴포넌트
   ├── charts/              # 차트 컴포넌트
   └── ui/                  # 재사용 UI 컴포넌트
   lib/
   ├── api.ts               # API 클라이언트
   └── utils.ts             # 유틸리티 함수
   types/
   └── index.ts             # TypeScript 타입 정의
   ```

4. **한국어 폰트 설정**
   - Pretendard 폰트 import
   - Tailwind config에 font family 추가

**성공 기준**:
- [ ] Next.js dev server 실행 가능 (`npm run dev`)
- [ ] TypeScript 컴파일 에러 없음
- [ ] 기본 페이지 렌더링 확인

---

### 2차 마일스톤: 백엔드 API 통합 (Priority: High)

**목표**: Python 백엔드와의 데이터 연결

**작업 항목**:

1. **Python FastAPI 서버 구현**
   - `src/ratestance/api/` 디렉토리 생성
   - FastAPI 애플리케이션 초기화 (`main.py`)
   - CORS 미들웨어 설정 (프론트엔드 도메인 허용)

2. **API 엔드포인트 구현** (`src/ratestance/api/routes.py`)
   ```python
   # /api/data/news-daily
   # /api/data/rate-series
   # /api/data/events
   # /api/data/event-study
   # /api/data/statistics
   ```
   - CSV 파일 읽기 (pandas)
   - JSON 형식으로 변환
   - 에러 핸들링

3. **프론트엔드 API 클라이언트** (`lib/api.ts`)
   - `fetch` wrapper 함수
   - TypeScript 타입 정의
   - 에러 처리

4. **TanStack Query 설정**
   - QueryClient 초기화
   - Provider 설정 (layout.tsx)
   - custom hooks 생성 (`useNewsDaily`, `useRateSeries`, 등)

**성공 기준**:
- [ ] FastAPI 서버 실행 가능 (`uvicorn src.ratestance.api.main:app --reload`)
- [ ] API 엔드포인트 JSON 응답 확인 (curl/브라우저)
- [ ] 프론트엔드에서 데이터 fetch 성공

---

### 3차 마일스톤: 주요 차트 컴포넌트 구현 (Priority: High)

**목표**: 4개 핵심 시각화 구현

**작업 항목**:

1. **뉴스 감성 시계열 차트** (`components/charts/NewsStanceTimeseries.tsx`)
   - Recharts LineChart 사용
   - X축: 날짜 (날짜 형식: YYYY-MM-DD)
   - Y축: 감성 점수 (-1.0 ~ +1.0)
   - 색상: 양수(빨강), 음수(파랑)
   - 이벤트 마커 (ReferenceLine)
   - Tooltip 커스터마이징
   - 반응형 크기 조정 (ResponsiveContainer)

2. **금리 시계열 차트** (`components/charts/RateSeriesChart.tsx`)
   - Recharts AreaChart 사용
   - Y축: 금리 (%)
   - 그라데이션 색상 채우기
   - Tooltip에 금리 값 표시

3. **이벤트 스터디 차트** (`components/charts/EventStudyChart.tsx`)
   - Recharts LineChart (다중 선)
   - 이벤트 유형별 색상 구분 (인상/인하/유지)
   - X축: -14일 ~ +14일
   - 신뢰 구간 표시 (Area, alpha=0.2)

4. **통계 카드** (`components/dashboard/StatCard.tsx`)
   - shadcn/ui Card 컴포넌트
   - 아이콘 + 라벨 + 값 구조
   - 호버 효과

**성공 기준**:
- [ ] 각 차트가 실제 데이터로 렌더링됨
- [ ] 차트 간 상호작용 없이 독립적으로 작동
- [ ] 반응형 레이아웃 (모바일/태블릿/데스크톱)

---

### 4차 마일스톤: 대시보드 레이아웃 및 인터랙션 (Priority: Medium)

**목표**: 전체 대시보드 조립 및 사용자 인터랙션

**작업 항목**:

1. **대시보드 메인 페이지** (`app/page.tsx`)
   - Grid 레이아웃 (Tailwind grid)
   - 컴포넌트 배치:
     ```
     [헤더: 타이틀 + 새로고침 버튼]
     [뉴스 차트 (70%) | 금리 차트 (30%)]
     [이벤트 스터디 차트 (100%)]
     [통계 카드 4개 (100%)]
     [뉴스 기사 리스트 (100%)]
     ```

2. **데이터 새로고침 기능**
   - "새로고침" 버튼 클릭 → TanStack Query `invalidateQueries`
   - 로딩 상태 표시 (Spinner)
   - 성공/실패 토스트 메시지

3. **이벤트 상세 패널** (`components/dashboard/EventDetailPanel.tsx`)
   - 사이드바 형태 (Dialog/Sheet)
   - 이벤트 정보: 날짜, 유형, 설명, 관련 뉴스 기사
   - 닫기 버튼

4. **뉴스 기사 리스트** (`components/dashboard/NewsList.tsx`)
   - 테이블 형태 (shadcn/ui Table)
   - 페이지네이션
   - 정렬 (날짜, 감성 점수)
   - 원본 기사 링크

**성공 기준**:
- [ ] 모든 컴포넌트가 한 페이지에 조립됨
- [ ] 데이터 새로고침 시 차트가 업데이트됨
- [ ] 이벤트 클릭 시 상세 패널 표시됨

---

### 5차 마일스톤: Stitch MCP 활용 UI 디자인 (Priority: Medium)

**목표**: Stitch MCP로 생성한 디자인 적용

**작업 항목**:

1. **Stitch MCP 호출**
   - 대시보드 레이아웃 디자인 요청
   - 차트 컴포넌트 스타일링 요청
   - 통계 카드 디자인 요청

2. **디자인 시스템 적용**
   - 색상 팔레트 (tailwind.config.js)
   - 타이포그래피 (font sizes, weights)
   - 간격 (spacing scale)
   - 둥근 모서리 (border-radius)
   - 그림자 (box-shadow)

3. **컴포넌트 스타일링**
   - shadcn/ui 컴포넌트 커스터마이징
   - 차트 스타일 오버라이드
   - 애니메이션 추가 (Framer Motion)

**성공 기준**:
- [ ] Stitch 생성 디자인이 실제 UI에 적용됨
- [ ] 일관된 스타일이 전체 앱에 적용됨
- [ ] Dark/Light 모드 전환 가능 (선택)

---

### 6차 마일스톤: 테스트 및 배포 준비 (Priority: Low)

**목표**: 품질 검증 및 프로덕션 빌드

**작업 항목**:

1. **테스트**
   - 컴포넌트 유닛 테스트 (Jest + React Testing Library)
   - API 통합 테스트
   - E2E 테스트 (Playwright)

2. **성능 최적화**
   - 번들 크기 분석 (Webpack Bundle Analyzer)
   - 코드 스플리팅 (dynamic import)
   - 이미지 최적화 (next/image)

3. **배포 설정**
   - Dockerfile 작성 (프론트엔드 + 백엔드)
   - docker-compose.yml
   - 환경 변수 설정 (.env.example)

**성공 기준**:
- [ ] 테스트 커버리지 80% 이상
- [ ] Lighthouse Performance 점수 90+ (Mobile)
- [ ] Docker 컨테이너 실행 가능

---

## Technical Approach

### 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (User)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Next.js 16 Frontend App                    │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────┐ │   │
│  │  │ Chart Components│  │ Dashboard UI │  │  API    │ │   │
│  │  │   (Recharts)    │  │ (shadcn/ui)  │  │ Client  │ │   │
│  │  └───────────────┘  └───────────────┘  └─────────┘ │   │
│  │         │                  │                  │       │   │
│  │         └──────────────────┴──────────────────┘       │   │
│  │                            │                          │   │
│  │                    TanStack Query                    │   │
│  └────────────────────────────┼──────────────────────────┘   │
│                               │                               │
│                               ▼                               │
│                      HTTP (REST API)                          │
└───────────────────────────────┼───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (Python 3.14)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           API Routes (src/ratestance/api/)            │  │
│  │  /api/data/news-daily  → CSV Reader → JSON Response   │  │
│  │  /api/data/rate-series → CSV Reader → JSON Response   │  │
│  │  /api/data/events       → CSV Reader → JSON Response   │  │
│  │  /api/data/event-study  → CSV Reader → JSON Response   │  │
│  │  /api/data/statistics   → Aggregator → JSON Response   │  │
│  └───────────────────────────────────────────────────────┘  │
│                               │                               │
│                               ▼                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Data Files (data/*.csv)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

1. **초기 로드**:
   ```
   User访问 "/" → Next.js page.tsx render
   → TanStack Query hooks execute
   → API Client fetch("/api/data/*")
   → FastAPI routes read CSV files
   → Return JSON data
   → Components re-render with data
   ```

2. **데이터 새로고침**:
   ```
   User clicks "Refresh" button
   → queryClient.invalidateQueries()
   → TanStack Query refetches all queries
   → Components update with new data
   → Toast message shows success/failure
   ```

3. **이벤트 상세 보기**:
   ```
   User clicks event marker
   → EventDetailPanel opens
   → Filter news articles by event date
   → Display event details
   ```

### 기술 스택 상세

**프론트엔드**:
- **Next.js 16**: React framework with App Router
- **TypeScript 5.9**: Type safety
- **Tailwind CSS 4**: Utility-first CSS
- **shadcn/ui**: Component library
- **Recharts 3**: Chart library
- **TanStack Query 5**: Data fetching
- **date-fns 4**: Date manipulation
- **Framer Motion 12**: Animation (선택)

**백엔드**:
- **Python 3.14**: Runtime
- **FastAPI 0.115**: Web framework (기존 스택 확장)
- **pandas 2.2**: Data processing (기존)
- **uvicorn**: ASGI server
- **pydantic 2.9**: Data validation (기존)

### 의사결정 기록

**Q1: 왜 Next.js를 선택했나?**
- A1: App Router, Server Components, SEO 최적화, 풍부한 생태계

**Q2: 왜 Recharts를 선택했나?**
- A2: React 친화적, 선언적 API, 커스터마이징 용이, TypeScript 지원

**Q3: 왜 shadcn/ui를 선택했나?**
- A3: 접근성, 모던 디자인, TypeScript 지원, Radix UI primitives

**Q4: 왜 TanStack Query를 선택했나?**
- A4: 캐싱, 자동 리페칭, 에러 핸들링, React 19 호환

**Q5: 백엔드를 FastAPI로 확장하는 이유는?**
- A5: 기존 Python 파이프라인과 통합, 자동 API 문서, 비동기 지원

## Risks & Mitigation

### 리스크 1: 기존 백엔드 파이프라인 수정 필요성

**확률**: Medium (50%)

**영향**: High

**완화 전략**:
- FastAPI를 기존 `src/ratestance/` 구조에 통합
- 새로운 `api/` 디렉토리만 추가 (기존 코드 수정 최소화)
- CSV 파일을 직접 읽는 엔드포인트 구현 (데이터베이스 불필요)

### 리스크 2: 차트 렌더링 성능 문제

**확률**: Medium (40%)

**영향**: Medium

**완화 전략**:
- 데이터 포인트 샘플링 (일별 → 주별)
- Virtual scrolling (뉴스 기사 리스트)
- React.memo()로 컴포넌트 최적화

### 리스크 3: 한국어 폰트 렌더링 문제

**확률**: Low (20%)

**영향**: Medium

**완화 전략**:
- Pretendard 폰트 사용 (한국어 최적화)
- 폰트 preload (next/font)
- Matplotlib과 동일한 폰트 설정 사용

### 리스크 4: Stitch MCP 디자인 품질 불확실성

**확률**: Medium (30%)

**영향**: Low

**완화 전략**:
- Stitch 디자인을 참고용으로 활용
- shadcn/ui 기본 컴포넌트로 fallback
- 수동 커스터마이징으로 디자인 수정

## Dependencies

### 내부 의존성

- **기존 파이프라인**: `src/ratestance/pipeline.py` 실행 → CSV 파일 생성
- **데이터 파일**: `data/*.csv` (최신 상태 유지 필요)

### 외부 의존성

- **ECOS API**: 금리 데이터 수집 (API 키 필요)
- **뉴스 RSS**: 뉴스 기사 수집 (인터넷 연결 필요)

## Estimate (Complexity-Based)

**전체 복잡도**: Medium-High

**작업 분류**:
- **단순**: 프로젝트 설정, API 라우팅 (1-2일)
- **보통**: 차트 컴포넌트 구현, 레이아웃 조립 (2-3일)
- **복잡**: 인터랙션 로직, 데이터 새로고침, 성능 최적화 (3-4일)

**총 예상 작업량**: 6-9일 (1인 기준)
