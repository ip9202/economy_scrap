#!/bin/bash
# RateStance API Server Startup Script
cd /Users/irons_server/projects/economy/api
source .venv/bin/activate
exec uvicorn ratestance.api.main:app --host 0.0.0.0 --port 8001
