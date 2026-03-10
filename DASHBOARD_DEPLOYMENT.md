# RateStance Dashboard 배포 가이드

> **Note**: 이 문서는 더 이상 업데이트되지 않습니다.
> 최신 배포 정보는 **[DEPLOYMENT.md](./DEPLOYMENT.md)**를 참조하세요.

---

## 빠른 참조

- **전체 배포 가이드**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **테스트 서버 포트 할당**: [DEPLOYMENT.md#test-server-port-allocation](./DEPLOYMENT.md#test-server-port-allocation)
- **서버 배포 절차**: [DEPLOYMENT.md#server-deployment-guide](./DEPLOYMENT.md#server-deployment-guide)
- **API 서버 관리**: [DEPLOYMENT.md#api-server-management](./DEPLOYMENT.md#api-server-management)

---

## 개요

Next.js standalone 빌드를 원격 서버에 배포하기 위한 표준 가이드입니다. Hanyang 프로젝트와 동일한 배포 패턴을 따릅니다.

### 배포 상태

| 항목 | 상태 |
|------|------|
| 서비스 URL | https://ip9202.site/economy |
| 대시보드 포트 | 3004 (PM2) |
| API 포트 | 8001 (PM2) |
| 웹 서버 | Nginx (HTTPS, HTTP/2) |

---

## 원클릭 배포

```bash
cd /Users/ip9202/develop/vibe/economy_scrap
./deploy/deploy.sh
```

---

## PM2 명령어 빠른 참조

```bash
# 서버에서 SSH 접속
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

---

<moai>DONE</moai>
