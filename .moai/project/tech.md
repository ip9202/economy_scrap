# 기술 스택

## 개요

이 문서는 economy_scrap 프로젝트의 기술 스택과 개발 환경을 정의합니다.

## 핵심 기술

### 주 언어

- **Python**: 3.11 이상 권장 (3.10 최소)
  - 타입 힌팅 지원
  - 성능 최적화
  - 최신 언어 기능 활용

## 웹 프레임워크 옵션

<!-- TODO: 아래 프레임워크 중 프로젝트에 적합한 것을 선택하고 나머지는 제거하세요 -->

### FastAPI (권장 - 고성능 API)

**장점**:
- 자동 API 문서 생성 (OpenAPI/Swagger)
- Pydantic을 통한 데이터 검증
- 비동기 처리 네이티브 지원
- 뛰어난 성능 (Starlette 기반)
- 타입 힌팅 완벽 지원

**설치**:
```bash
pip install fastapi[all] uvicorn[standard]
```

**사용 사례**:
- RESTful API 서버
- 마이크로서비스
- 실시간 데이터 처리
- 머신러닝 모델 서빙

### Flask (권장 - 유연성 및 간결함)

**장점**:
- 간단하고 직관적인 API
- 풍부한 확장 생태계
- 유연한 구조
- 작은 학습 곡선

**설치**:
```bash
pip install Flask Flask-SQLAlchemy Flask-Migrate
```

**사용 사례**:
- 중소규모 웹 애플리케이션
- 프로토타입 개발
- 관리자 대시보드
- 간단한 REST API

### Django (권장 - 풀스택 프레임워크)

**장점**:
- 배터리 포함 (ORM, Admin, Auth 내장)
- 강력한 보안 기능
- 대규모 프로젝트에 적합
- 성숙한 생태계

**설치**:
```bash
pip install Django djangorestframework
```

**사용 사례**:
- 대규모 웹 애플리케이션
- CMS 및 데이터 중심 사이트
- 복잡한 비즈니스 로직
- 관리자 패널이 필요한 프로젝트

## 데이터베이스

<!-- TODO: 프로젝트에 적합한 데이터베이스를 선택하세요 -->

### 관계형 데이터베이스 (RDBMS)

**PostgreSQL** (권장):
- 강력한 ACID 보장
- 풍부한 데이터 타입
- JSON 지원
- 확장성 및 성능

```bash
pip install psycopg2-binary  # PostgreSQL 어댑터
```

**MySQL/MariaDB**:
- 널리 사용되는 오픈소스 DB
- 간단한 설정
- 좋은 성능

```bash
pip install mysqlclient  # MySQL 어댑터
```

**SQLite**:
- 파일 기반 경량 DB
- 설정 불필요
- 개발 및 테스트에 적합

### NoSQL 데이터베이스

**MongoDB**:
- 유연한 스키마
- 문서 기반 저장
- 수평 확장 용이

```bash
pip install pymongo motor  # Async MongoDB
```

**Redis**:
- 인메모리 키-값 저장소
- 캐싱 및 세션 관리
- 실시간 데이터 처리

```bash
pip install redis aioredis
```

## ORM (Object-Relational Mapping)

<!-- TODO: ORM 라이브러리 선택 -->

### SQLAlchemy (권장)

**특징**:
- 강력하고 유연한 ORM
- 비동기 지원 (SQLAlchemy 2.0+)
- 복잡한 쿼리 지원

```bash
pip install sqlalchemy alembic  # 마이그레이션 도구
```

### Django ORM

**특징**:
- Django 내장 ORM
- 간단한 API
- 자동 관리자 인터페이스

## 개발 도구 및 의존성

### 필수 개발 도구

**의존성 관리**:
```bash
pip install poetry  # 현대적 의존성 관리 (권장)
# 또는
pip install pip-tools  # requirements.txt 관리
```

**코드 품질**:
```bash
pip install ruff black isort mypy
```

- **Ruff**: 빠른 Python 린터
- **Black**: 코드 포매터
- **isort**: Import 정렬
- **mypy**: 타입 체크

**테스트**:
```bash
pip install pytest pytest-cov pytest-asyncio
```

- **pytest**: 테스트 프레임워크
- **pytest-cov**: 커버리지 리포트
- **pytest-asyncio**: 비동기 테스트

### 추가 유틸리티

**환경 변수 관리**:
```bash
pip install python-dotenv
```

**데이터 검증**:
```bash
pip install pydantic
```

**HTTP 클라이언트**:
```bash
pip install httpx aiohttp
```

**날짜/시간 처리**:
```bash
pip install python-dateutil
```

## 프론트엔드 (선택 사항)

<!-- TODO: 프론트엔드가 필요한 경우 선택 -->

### 템플릿 엔진

**Jinja2** (Flask, FastAPI):
- 강력한 템플릿 언어
- 자동 이스케이핑
- 템플릿 상속

**Django Templates**:
- Django 내장 템플릿 엔진
- 간단하고 안전

### JavaScript 프레임워크 통합

프론트엔드 분리 시:
- **React**: 컴포넌트 기반 UI
- **Vue.js**: 점진적 프레임워크
- **Svelte**: 컴파일 기반 프레임워크

## 배포 및 운영

### ASGI/WSGI 서버

**Uvicorn** (FastAPI, Starlette):
```bash
pip install uvicorn[standard]
```

**Gunicorn** (Flask, Django):
```bash
pip install gunicorn
```

### 컨테이너화

**Docker**:
- 일관된 개발/운영 환경
- 쉬운 배포 및 확장

**docker-compose**:
- 로컬 개발 환경 오케스트레이션
- 다중 서비스 관리

### CI/CD

**GitHub Actions** (권장):
- 무료 CI/CD
- GitHub 네이티브 통합
- 간단한 YAML 설정

**GitLab CI/CD**:
- 자체 호스팅 가능
- 강력한 파이프라인

## 보안

### 인증 및 인가

**JWT (JSON Web Token)**:
```bash
pip install pyjwt python-jose[cryptography]
```

**OAuth 2.0**:
```bash
pip install authlib
```

### 암호화

**Passlib**:
```bash
pip install passlib[bcrypt]
```

### 환경 변수 및 시크릿 관리

- **python-dotenv**: 로컬 개발
- **환경 변수**: 운영 환경
- **AWS Secrets Manager / HashiCorp Vault**: 프로덕션 시크릿

## 모니터링 및 로깅

### 로깅

**Python logging**:
- 표준 라이브러리
- 다양한 핸들러

**Loguru** (권장):
```bash
pip install loguru
```
- 간단한 API
- 자동 로테이션
- 컬러 출력

### 모니터링

**Prometheus + Grafana**:
- 메트릭 수집 및 시각화

**Sentry**:
```bash
pip install sentry-sdk
```
- 에러 추적 및 모니터링

## 개발 환경 설정

### Python 버전 관리

**pyenv** (권장):
```bash
# macOS
brew install pyenv

# 사용법
pyenv install 3.11.7
pyenv local 3.11.7
```

### 가상 환경

**venv** (내장):
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Poetry** (권장):
```bash
poetry install
poetry shell
```

### 에디터 및 IDE

**VS Code** (권장):
- Python 확장 설치
- Pylance (타입 체크)
- Ruff 확장

**PyCharm**:
- 강력한 Python IDE
- 통합 디버거
- 데이터베이스 도구

## 프로젝트 초기 설정

### 1. pyproject.toml 생성

```bash
# Poetry 사용
poetry init

# 수동 작성도 가능
```

### 2. 의존성 설치

```bash
# 기본 의존성
pip install fastapi uvicorn sqlalchemy alembic pydantic python-dotenv

# 개발 의존성
pip install --dev pytest pytest-cov ruff black mypy
```

### 3. 설정 파일 작성

- `.env.example`: 환경 변수 템플릿
- `.gitignore`: Python 표준 ignore 패턴
- `pyproject.toml`: 프로젝트 메타데이터

### 4. 데이터베이스 마이그레이션

```bash
# Alembic 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

## 성능 최적화

### 비동기 처리

- **asyncio**: 네이티브 비동기 지원
- **aiohttp**: 비동기 HTTP 클라이언트
- **aiomysql/asyncpg**: 비동기 DB 드라이버

### 캐싱

- **Redis**: 분산 캐싱
- **functools.lru_cache**: 메모이제이션
- **aiocache**: 비동기 캐싱

### 데이터베이스 최적화

- 인덱스 적절히 활용
- N+1 쿼리 문제 해결 (eager loading)
- 커넥션 풀링

## 테스트 전략

### 테스트 레벨

**단위 테스트**:
- 개별 함수/메서드 테스트
- 빠른 실행
- 격리된 환경

**통합 테스트**:
- API 엔드포인트 테스트
- 데이터베이스 통합
- 실제 의존성 사용

**E2E 테스트**:
- 전체 사용자 플로우
- Selenium, Playwright 사용

### 테스트 커버리지 목표

- 최소 85% 코드 커버리지
- 핵심 비즈니스 로직 100%
- CI/CD 파이프라인에서 자동 실행

## 버전 관리 전략

### Git 브랜치 전략

**Git Flow** (권장):
- `main`: 프로덕션 배포
- `develop`: 개발 통합
- `feature/*`: 기능 개발
- `hotfix/*`: 긴급 수정

### 커밋 메시지 규칙

**Conventional Commits**:
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `docs:` 문서 변경
- `style:` 코드 스타일 (포매팅)
- `refactor:` 리팩토링
- `test:` 테스트 추가/수정
- `chore:` 빌드, 설정 변경

## 참고 자료

### 공식 문서

- [Python 공식 문서](https://docs.python.org/3/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Flask 문서](https://flask.palletsprojects.com/)
- [Django 문서](https://docs.djangoproject.com/)

### 학습 자료

- [Real Python](https://realpython.com/)
- [Full Stack Python](https://www.fullstackpython.com/)
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/)

### 커뮤니티

- [Python Korea 커뮤니티](https://pythonkorea.github.io/)
- [Stack Overflow - Python](https://stackoverflow.com/questions/tagged/python)

---

*이 기술 스택은 프로젝트 요구사항에 따라 조정될 수 있습니다. TODO 섹션을 채우고 불필요한 옵션은 제거해주세요.*
