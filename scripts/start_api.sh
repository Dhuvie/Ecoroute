#!/bin/bash
# EcoRoute API server launcher - fully detached
cd /home/z/my-project/ecoroute/backend
exec /home/z/.venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1
