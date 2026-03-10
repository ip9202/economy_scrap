# Deploy Folder

## 개요

이 폴더는 RateStance Dashboard 및 API 배포를 위한 스크립트와 설정 파일들을 포함합니다.

## 빠른 시작

```bash
# Dashboard 배포
./deploy/deploy.sh

# Root index.html 배포
./deploy/deploy-index.sh
```

## 파일 목록

| 파일 | 설명 |
|------|------|
| `deploy.sh` | 메인 배포 스크립트 (dashboard 배포) |
| `deploy-index.sh` | Root index.html 배포 스크립트 |
| `start-api.sh` | API 서버 시작 스크립트 (포트 8001) |
| `ecosystem.config.json` | PM2 API 설정 파일 |
| `nginx-economy.conf` | Nginx 설정 템플릿 |
| `index.html` | Root 페이지 HTML 템플릿 |

## 상세 문서

모든 배포 관련 문서는 상위 DEPLOYMENT.md를 참조하세요:

- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - 전체 배포 가이드
  - 서버 설정 정보
  - 초기 설정 절차
  - 배포 절차
  - 문제 해결 가이드
  - Nginx 설정

## 주요 명령어

### 배포

```bash
# Dashboard 배포
./deploy/deploy.sh

# Root index.html 배포
./deploy/deploy-index.sh
```

### 서버 관리

```bash
# SSH 접속
ssh irons_server@ip9202.site

# PM2 프로세스 목록
pm2 list

# Dashboard 재시작
pm2 restart ratestance

# API 재시작
pm2 restart ratestance-api

# 로그 확인
pm2 logs ratestance --lines 50
pm2 logs ratestance-api --lines 50
```

## 설정 요약

| 설정 | Dashboard | API |
|------|-----------|-----|
| PM2 이름 | `ratestance` | `ratestance-api` |
| 포트 | `3004` | `8001` |
| URL | `/economy` | `/api/` |
