#!/bin/bash
# Development startup script for RateStance Dashboard
# This script starts both the FastAPI backend and Next.js frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}RateStance Dashboard Development Server${NC}"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    echo -e "${GREEN}All servers stopped.${NC}"
}

trap cleanup EXIT INT TERM

# Check if data files exist
echo -e "${YELLOW}Checking data files...${NC}"
if [ ! -f "data/news_daily.csv" ]; then
    echo -e "${RED}Error: Data files not found. Please run the pipeline first:${NC}"
    echo "  python -m ratestance.cli run"
    exit 1
fi
echo -e "${GREEN}Data files found.${NC}"
echo ""

# Start FastAPI backend
echo -e "${YELLOW}Starting FastAPI backend on http://localhost:8000${NC}"
/Users/ip9202/develop/vibe/economy_scrap/.venv/bin/python -m uvicorn ratestance.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}Error: Backend failed to start. Check logs above.${NC}"
    exit 1
fi
echo -e "${GREEN}Backend started successfully!${NC}"
echo ""

# Start Next.js frontend
echo -e "${YELLOW}Starting Next.js frontend on http://localhost:3000${NC}"
cd dashboard
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}=========================================="
echo -e "Both servers are running!"
echo -e "==========================================${NC}"
echo ""
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for any process to exit
wait
