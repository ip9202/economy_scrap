# 프로젝트 구조

## 권장 디렉토리 구조

이 문서는 Python 웹 애플리케이션을 위한 권장 디렉토리 구조를 설명합니다.

## 표준 프로젝트 레이아웃

```
economy_scrap/
├── src/                          # 소스 코드 디렉토리
│   └── economy_scrap/            # 메인 애플리케이션 패키지
│       ├── __init__.py           # 패키지 초기화 파일
│       ├── main.py               # 애플리케이션 진입점
│       ├── config.py             # 설정 관리
│       ├── api/                  # API 라우트 및 엔드포인트
│       │   ├── __init__.py
│       │   ├── routes.py         # API 라우트 정의
│       │   └── dependencies.py   # 의존성 주입
│       ├── core/                 # 핵심 비즈니스 로직
│       │   ├── __init__.py
│       │   └── business.py       # 비즈니스 로직
│       ├── models/               # 데이터 모델
│       │   ├── __init__.py
│       │   └── schemas.py        # Pydantic 스키마
│       ├── db/                   # 데이터베이스 관련
│       │   ├── __init__.py
│       │   ├── database.py       # DB 연결 설정
│       │   └── models.py         # ORM 모델
│       └── utils/                # 유틸리티 함수
│           ├── __init__.py
│           └── helpers.py        # 헬퍼 함수
│
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py               # pytest 설정
│   ├── unit/                     # 단위 테스트
│   │   ├── __init__.py
│   │   └── test_core.py
│   └── integration/              # 통합 테스트
│       ├── __init__.py
│       └── test_api.py
│
├── docs/                         # 문서
│   ├── api/                      # API 문서
│   ├── guides/                   # 사용 가이드
│   └── architecture.md           # 아키텍처 문서
│
├── config/                       # 설정 파일
│   ├── development.yaml          # 개발 환경 설정
│   ├── production.yaml           # 운영 환경 설정
│   └── test.yaml                 # 테스트 환경 설정
│
├── static/                       # 정적 파일
│   ├── css/                      # 스타일시트
│   ├── js/                       # JavaScript 파일
│   └── images/                   # 이미지 파일
│
├── templates/                    # HTML 템플릿 (Jinja2 등)
│   ├── base.html                 # 베이스 템플릿
│   └── pages/                    # 페이지 템플릿
│
├── scripts/                      # 유틸리티 스크립트
│   ├── setup.sh                  # 초기 설정 스크립트
│   └── migrate.py                # 데이터베이스 마이그레이션
│
├── .moai/                        # MoAI-ADK 설정 (자동 생성)
│   ├── config/                   # MoAI 설정
│   ├── specs/                    # SPEC 문서
│   └── project/                  # 프로젝트 문서 (현재 위치)
│
├── .github/                      # GitHub 설정
│   └── workflows/                # CI/CD 워크플로우
│       └── ci.yml
│
├── pyproject.toml                # 프로젝트 메타데이터 및 의존성
├── requirements.txt              # 의존성 목록 (pip)
├── requirements-dev.txt          # 개발 의존성
├── .env.example                  # 환경 변수 예제
├── .gitignore                    # Git 제외 파일
├── README.md                     # 프로젝트 개요
├── CHANGELOG.md                  # 변경 이력
└── LICENSE                       # 라이선스

```

## 주요 디렉토리 설명

### src/ - 소스 코드

애플리케이션의 모든 소스 코드를 포함합니다.

**목적**: 프로덕션 코드와 테스트 코드 분리

**구조 원칙**:
- 도메인 주도 설계(DDD) 패턴 사용 권장
- 계층별로 명확한 책임 분리
- 순환 의존성 방지

**하위 디렉토리**:
- `api/`: REST API 엔드포인트 정의
- `core/`: 비즈니스 로직 및 도메인 모델
- `models/`: 데이터 모델 및 스키마
- `db/`: 데이터베이스 연결 및 ORM 모델
- `utils/`: 공통 유틸리티 함수

### tests/ - 테스트 코드

모든 테스트 코드를 포함합니다.

**목적**: 코드 품질 보장 및 버그 예방

**테스트 전략**:
- 단위 테스트(unit/): 개별 함수/클래스 테스트
- 통합 테스트(integration/): API 및 DB 통합 테스트
- E2E 테스트(e2e/): 전체 시스템 테스트 (필요시)

**권장 사항**:
- pytest 프레임워크 사용
- 최소 85% 코드 커버리지 목표
- CI/CD 파이프라인에 자동 테스트 통합

### docs/ - 문서

프로젝트 문서를 포함합니다.

**목적**: 개발자 및 사용자를 위한 문서 제공

**문서 종류**:
- API 문서: OpenAPI/Swagger 스펙
- 아키텍처 문서: 시스템 설계 설명
- 사용 가이드: 설치 및 사용법
- 개발 가이드: 개발 환경 설정 및 기여 방법

### config/ - 설정 파일

환경별 설정 파일을 포함합니다.

**목적**: 환경별 설정 분리 및 관리

**설정 파일**:
- `development.yaml`: 로컬 개발 환경
- `production.yaml`: 운영 환경
- `test.yaml`: 테스트 환경

**보안 주의사항**:
- 민감한 정보는 환경 변수로 관리
- `.env` 파일은 `.gitignore`에 추가
- `.env.example`로 필요한 환경 변수 명시

### static/ - 정적 파일

CSS, JavaScript, 이미지 등 정적 리소스를 포함합니다.

**목적**: 웹 애플리케이션 리소스 관리

**구조**:
- `css/`: 스타일시트
- `js/`: 클라이언트 측 JavaScript
- `images/`: 이미지 파일
- `fonts/`: 웹 폰트 (필요시)

### templates/ - HTML 템플릿

서버 측 렌더링을 위한 HTML 템플릿을 포함합니다.

**목적**: 동적 HTML 페이지 생성

**템플릿 엔진**:
- Jinja2 (Flask)
- Django Templates (Django)

**구조**:
- `base.html`: 공통 레이아웃
- `components/`: 재사용 가능한 컴포넌트
- `pages/`: 개별 페이지 템플릿

### scripts/ - 유틸리티 스크립트

개발 및 배포를 위한 스크립트를 포함합니다.

**목적**: 반복 작업 자동화

**스크립트 예시**:
- 데이터베이스 마이그레이션
- 초기 데이터 생성
- 배포 자동화
- 백업 및 복구

## 프레임워크별 권장 구조

### FastAPI 프로젝트

FastAPI 사용 시 권장 구조:

```
src/economy_scrap/
├── main.py                 # FastAPI 앱 생성 및 라우터 등록
├── api/
│   ├── v1/                 # API 버전 관리
│   │   ├── __init__.py
│   │   ├── endpoints/      # 엔드포인트 그룹
│   │   │   ├── users.py
│   │   │   └── items.py
│   │   └── dependencies.py # 의존성 주입
├── core/
│   ├── config.py           # 설정 (pydantic BaseSettings)
│   └── security.py         # 인증/인가
├── models/
│   ├── domain.py           # 도메인 모델
│   └── schemas.py          # Pydantic 스키마
└── db/
    ├── base.py             # SQLAlchemy Base
    ├── session.py          # DB 세션
    └── models.py           # ORM 모델
```

### Flask 프로젝트

Flask 사용 시 권장 구조:

```
src/economy_scrap/
├── __init__.py             # Flask 앱 팩토리
├── app.py                  # 앱 진입점
├── blueprints/             # Flask Blueprints
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
├── models/                 # SQLAlchemy 모델
├── forms/                  # WTForms
└── static/                 # 정적 파일
```

### Django 프로젝트

Django 사용 시 기본 구조 활용:

```
economy_scrap/              # 프로젝트 루트
├── manage.py
├── economy_scrap/          # 프로젝트 설정
│   ├── settings/           # 환경별 설정
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
└── apps/                   # Django 앱들
    ├── users/
    ├── core/
    └── api/
```

## 베스트 프랙티스

### 1. 패키지 구조

- **단일 책임 원칙**: 각 모듈은 하나의 명확한 목적
- **계층 분리**: API, 비즈니스 로직, 데이터 레이어 분리
- **순환 참조 방지**: 명확한 의존성 방향 유지

### 2. 설정 관리

- **환경별 설정**: development, test, production 분리
- **환경 변수**: 민감한 정보는 환경 변수로 관리
- **기본값 제공**: 개발 편의를 위한 합리적인 기본값

### 3. 테스트

- **테스트 격리**: 각 테스트는 독립적으로 실행 가능
- **픽스처 활용**: 공통 테스트 데이터는 conftest.py에서 관리
- **모의 객체**: 외부 의존성은 mock으로 처리

### 4. 문서화

- **코드 문서화**: Docstring 작성 (Google/NumPy 스타일)
- **API 문서**: OpenAPI/Swagger 자동 생성
- **README**: 설치, 실행, 테스트 방법 명시

### 5. 버전 관리

- **의미론적 버저닝**: MAJOR.MINOR.PATCH 형식
- **변경 이력**: CHANGELOG.md 유지
- **태그 활용**: Git 태그로 릴리스 관리

## 파일 위치 참조

### 설정 파일

- **의존성 관리**: `pyproject.toml` 또는 `requirements.txt`
- **환경 설정**: `config/*.yaml` 또는 `.env`
- **Git 설정**: `.gitignore`, `.gitattributes`
- **CI/CD**: `.github/workflows/*.yml`

### 실행 파일

- **메인 진입점**: `src/economy_scrap/main.py`
- **WSGI/ASGI**: `src/economy_scrap/wsgi.py` 또는 `asgi.py`
- **CLI**: `src/economy_scrap/cli.py` (필요시)

### 문서 파일

- **프로젝트 개요**: `README.md` (루트)
- **API 문서**: `docs/api/openapi.yaml`
- **변경 이력**: `CHANGELOG.md`
- **기여 가이드**: `CONTRIBUTING.md` (오픈소스인 경우)

---

*이 구조는 권장 사항이며, 프로젝트 특성에 맞게 조정할 수 있습니다.*
