# System Health Suite

A monitoring system with:

- **Agent**: collects machine health info
- **Server (FastAPI)**: stores reports
- **Dashboard (React)**: shows machine status

## Features

- Supports different OS
- add more

## Setup

### Backend (FastAPI)

cd server
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic

<!-- $env:API_KEY="DEV_AGENT_KEY" -->
<!-- uvicorn app:app --reload --host 0.0.0.0 --port 8000 -->

uvicorn app:app --reload --port 8000

### Frontend (React)

cd dashboard
npm install
npm install axios
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm run dev

### Agent

cd agent
python -m venv .venv
.venv\Scripts\activate
pip install requests
python agent.py

#### if you want installer to run automatically!

pip install pyinstaller
pyinstaller --onefile agent.py -n syshealth-agent

ctrl + R
powershell
ctrl + Shift + Enter (for admin)
cd C:\Users\username
cd system_health_suite/agent/install/windows
.\install.ps1

#### for testing, you can directly ingest as well

cd system_health_suite
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ingest" `  -Method POST`
-Headers @{ "Content-Type" = "application/json"; "Authorization" = "Bearer DEV_AGENT_KEY" } `
-Body '{
"machine_id": "test123",
"hostname": "Lakshya-PC",
"os": {"system": "Windows", "release": "10", "version": "22H2", "architecture": "x64"},
"checks": {"disk_encryption": true, "antivirus": true},
"issues": {"unencrypted_disk": false, "outdated_os": false, "no_antivirus": false, "idle_sleep_too_high": true},
"timestamp": "2025-08-16T12:45:00"
}'
