# RateStance Deployment Guide

**Version**: 0.1.0
**Status**: DEPLOYED
**Last Updated**: 2026-02-02
**Test Coverage**: 93.24% (50/50 tests passing)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Status](#deployment-status)
3. [Server Configuration](#server-configuration)
4. [Deployment Procedures](#deployment-procedures)
5. [Initial Server Setup](#initial-server-setup)
6. [Troubleshooting](#troubleshooting)
7. [Project Information](#project-information)

---

## Quick Start

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd economy_scrap

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and add your ECOS_API_KEY from https://ecos.bok.or.kr/api/
```

### Dashboard Deployment

```bash
cd /Users/ip9202/develop/vibe/economy_scrap
./deploy/deploy.sh
```

### Root Page Deployment

```bash
# Method 1: Interactive (password prompt)
./deploy/deploy-index.sh

# Method 2: Environment variable
DEPLOY_PASS=rkdcjfIP00! ./deploy/deploy-index.sh
```

---

## Deployment Status

| 항목 | 상태 |
|------|------|
| 서비스 URL | https://ip9202.site/economy |
| API URL | https://ip9202.site/api/ |
| 대시보드 포트 | 3004 (PM2: ratestance) |
| API 포트 | 8001 (PM2: ratestance-api) |
| 웹 서버 | Nginx (HTTPS, HTTP/2) |
| 최종 배포일 | 2026-02-02 |

---

## Server Configuration

### Port Allocation

| Port | Service | Type | PM2 Name | Purpose | URL |
|------|---------|------|----------|---------|-----|
| **8001** | ratestance-api | Python/FastAPI | `ratestance-api` | 금융 뉴스 분석 API | `/api/` |
| **3004** | ratestance | Next.js | `ratestance` | 금융 뉴스 분석 대시보드 | `/economy` |

### Server Information

```bash
# Server Connection
SERVER_HOST="ip9202.site"
SERVER_USER="irons_server"
PROJECT_PATH="~/projects/economy"

# RateStance Dashboard
APP_PORT="3004"
PM2_NAME="ratestance"
SERVICE_URL="https://ip9202.site/economy"
BASE_PATH="/economy"

# RateStance API
API_PORT="8001"
API_PM2_NAME="ratestance-api"
API_PATH="/api/"
```

### Port Management Commands

```bash
# Check port usage
lsof -i :8001  # ratestance-api
lsof -i :3004  # ratestance dashboard

# PM2 process list
pm2 list

# PM2 logs
pm2 logs ratestance --lines 20
pm2 logs ratestance-api --lines 20
```

---

## Deployment Procedures

### 1. Dashboard Deployment

#### Build Structure

After `npm run build`, the structure is:

```
.next/
├── standalone/           # standalone build
│   ├── server.js        # server entry point
│   ├── package.json     # minimal dependencies
│   └── .next/           # actual build output ← Deploy this!
├── static/              # static files ← Deploy separately!
```

#### One-Click Deployment

```bash
cd /Users/ip9202/develop/vibe/economy_scrap
./deploy/deploy.sh
```

#### Deployment Steps

1. **Build** - Next.js application build
2. **Clear server cache** - Remove old .next folder
3. **Deploy .next** - Upload .next folder contents
4. **Deploy static** - Upload static folder
5. **Restart PM2** - Restart ratestance process
6. **Check logs** - Verify startup

### 2. Root Index.html Deployment

```bash
cd /Users/ip9202/develop/vibe/economy_scrap

# Method 1: Interactive (password prompt)
./deploy/deploy-index.sh

# Method 2: Environment variable
DEPLOY_PASS=rkdcjfIP00! ./deploy/deploy-index.sh
```

### 3. API Server Management

#### PM2 Commands

```bash
# SSH to server
ssh irons_server@ip9202.site

# PM2 process list
pm2 list

# Start ratestance-api
cd ~/projects/economy/api
pm2 start ecosystem.config.json
pm2 save

# Restart ratestance-api
pm2 restart ratestance-api

# Stop ratestance-api
pm2 stop ratestance-api

# View logs
pm2 logs ratestance-api --lines 50

# Real-time logs
pm2 logs ratestance-api
```

#### API Endpoints

| Endpoint | Description |
|-----------|-------------|
| `/api/data/statistics` | Statistics data |
| `/api/data/news-daily` | Daily news sentiment data |
| `/api/data/rate-series` | Interest rate time series |
| `/api/data/events` | Rate change events |
| `/api/data/event-study` | Event study analysis |
| `/api/data/news-articles` | News articles list |

---

## Initial Server Setup

### One-Time Dashboard Setup

```bash
# SSH to server
ssh irons_server@ip9202.site

# Create project directory
mkdir -p ~/projects/economy

# Copy from local after build:
# 1. .next/standalone/server.js → ~/projects/economy/server.js
# 2. .next/standalone/package.json → ~/projects/economy/package.json

# Install dependencies
cd ~/projects/economy
npm install

# Register PM2 process
PORT=3004 pm2 start server.js --name ratestance
pm2 save
```

### One-Time API Setup

```bash
# SSH to server
ssh irons_server@ip9202.site

# Create API project directory
mkdir -p ~/projects/economy/api

# Copy ecosystem.config.json to ~/projects/economy/api/

# Create virtual environment
cd ~/projects/economy/api
python3.11 -m venv .venv
source .venv/bin/activate

# Install package (from local project)
pip install -e /path/to/economy_scrap[api]

# Register PM2 process
pm2 start ecosystem.config.json
pm2 save
```

### Nginx Configuration

Nginx 설정 파일 위치: `/opt/homebrew/etc/nginx/nginx.conf`

```nginx
# RateStance static resources
location /economy/_next/ {
    proxy_pass http://127.0.0.1:3004;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# RateStance main page
location /economy {
    proxy_pass http://127.0.0.1:3004/;
    rewrite ^/economy(/.*)$ $1 break;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# RateStance API
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # CORS headers
    add_header Access-Control-Allow-Origin "https://ip9202.site" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept" always;

    if ($request_method = OPTIONS) {
        return 204;
    }
}
```

#### Nginx Restart Commands

```bash
# Homebrew nginx restart
brew services restart nginx

# Check nginx status
ps aux | grep nginx | grep -v grep
```

---

## Troubleshooting

### Port Conflicts

```bash
# Check if port is in use
lsof -i :3004  # Dashboard port
lsof -i :8001  # API port

# Kill process if needed
kill -9 <PID>
```

### PM2 Issues

```bash
# Check process status
pm2 list

# View error logs
pm2 logs ratestance --err
pm2 logs ratestance-api --err

# Restart process
pm2 restart ratestance
pm2 restart ratestance-api

# Reset PM2 (if needed)
pm2 delete all
pm2 save
```

### Build Issues

```bash
# Clear Next.js cache
cd dashboard
rm -rf .next

# Rebuild
npm run build
```

### Common Issues

**Build fails**
- Ensure `output: 'standalone'` in `dashboard/next.config.ts`
- Check Node.js version compatibility

**API not responding**
- Check if PM2 process is running: `pm2 list`
- Verify port 8001 is available: `lsof -i :8001`
- Check logs: `pm2 logs ratestance-api`

**Dashboard not loading**
- Check if PM2 process is running: `pm2 list`
- Verify port 3004 is available: `lsof -i :3004`
- Check Nginx configuration

**404 errors on /economy (basePath 관련)**
- Next.js `basePath: '/economy'` 설정 시, Nginx에서 `rewrite`로 경로를 벗겨내면 안 됨
- 올바른 설정: `proxy_pass http://127.0.0.1:3004;` (trailing slash 없이)
- 잘못된 설정: `proxy_pass http://127.0.0.1:3004/;` + `rewrite ^/economy(/.*)$ $1 break;`
- Next.js는 `basePath`가 있으면 `/economy` 경로 그대로 받아야 정상 동작
- 참고: `hanyang` 프로젝트는 `basePath` 없이 동작하므로 rewrite 패턴이 맞지만, `ratestance`는 다름

**API 서버 502 에러 (ratestance-api 미실행)**
- `pm2 list`에서 ratestance-api 프로세스 존재 여부 확인
- 프로세스 없으면: `cd ~/projects/economy/api && pm2 start ecosystem.config.json && pm2 save`
- PM2 프로세스가 서버 재부팅 후 사라질 수 있으므로 `pm2 save`로 저장 필수

---

## Project Information

### File Structure

```
economy_scrap/
├── dashboard/              # Next.js application
│   ├── next.config.ts     # standalone output setting
│   ├── package.json
│   └── ...
├── deploy/                # Deployment scripts and configs
│   ├── deploy.sh          # Main dashboard deployment script
│   ├── deploy-index.sh    # Root index.html deployment
│   ├── start-api.sh       # API server startup script (port 8001)
│   ├── ecosystem.config.json  # PM2 config for API
│   ├── nginx-economy.conf # Nginx configuration template
│   ├── index.html         # Root page template
│   └── README.md          # Deploy folder documentation
├── src/ratestance/        # Python API source
│   └── api/               # FastAPI application
│       ├── main.py        # API entry point
│       ├── routes.py      # API endpoints
│       └── ...
└── DEPLOYMENT.md          # This file (unified documentation)
```

### Deployment Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy.sh` | Dashboard 배포 | `./deploy/deploy.sh` |
| `deploy-index.sh` | Root index.html 배포 | `./deploy/deploy-index.sh` |
| `start-api.sh` | API 서버 시작 (서버에서 실행) | PM2 통해 관리 |

### Important Notes

1. **고정 포트 사용**: ratestance는 항상 포트 3004, ratestance-api는 항상 포트 8001 사용
2. **포트 충돌 확인**: 서비스 시작 전 `lsof -i :PORT`로 포트 사용 확인
3. **Nginx 설정**: 서버에 `/_next/`, `/economy`, `/api/` location block 필요
4. **PM2 설정**: 서버에 `ratestance`, `ratestance-api` 프로세스 미리 등록 필요
5. **권한**: 배포 스크립트에 실행 권한 필요 (`chmod +x deploy/*.sh`)

### Nginx 설정 주의사항 (basePath)

Next.js `basePath: '/economy'`를 사용할 때 Nginx 설정:

```nginx
# 올바른 설정 (basePath 사용 시)
location /economy {
    proxy_pass http://127.0.0.1:3004;    # trailing slash 없음
    # rewrite 없음 - /economy 경로를 그대로 전달
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

`basePath`가 없는 프로젝트(예: hanyang)는 `proxy_pass` trailing slash + `rewrite`가 필요하지만, `basePath`가 있으면 경로를 그대로 전달해야 함.

### Update History

- **2026-03-10**: Nginx 404 에러 수정 및 API 서버 복구
  - /economy 404 원인: Nginx rewrite가 basePath를 제거하여 Next.js가 인식 못함
  - 수정: proxy_pass trailing slash 제거 + rewrite 규칙 삭제
  - ratestance-api PM2 프로세스 재등록 (포트 8001)

- **2026-02-02**: Deployment documentation unified and reorganized
  - Consolidated all deployment information into DEPLOYMENT.md
  - Added comprehensive troubleshooting section
  - Organized deployment procedures

- **2026-02-01**: Dashboard deployment setup complete
  - Applied Hanyang project deployment pattern
  - Standalone build configuration
  - Deployment scripts created
  - Added RateStance to root index.html

- **2026-02-01**: API server configuration and port allocation documented
  - ratestance-api service added (port 8001)
  - PM2 ecosystem.config.json setup
  - Complete test server port allocation table
  - Nginx API proxy configuration added

---

<moai>DONE</moai>
