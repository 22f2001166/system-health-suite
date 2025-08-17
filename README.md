# System Health Suite

A complete monitoring system for tracking the **health and security posture of machines**.

- **Agent (Python)**: collects machine health info
- **Server (FastAPI + SQLAlchemy)**: stores reports and exposes API
- **Dashboard (React + MUI)**: shows machine status, provides filtering/sorting, and CSV exports.

## Features

- Generates a unique **machine ID** for each device.
- Collects:
  - **OS detection** (Windows/Linux/macOS), with **Windows 11 detection** via build number.
  - **Disk encryption status** (BitLocker, FileVault, LUKS/dm-crypt).
  - **Pending OS updates** (Windows Update, apt, dnf, pacman, macOS Software Update).
  - **Antivirus status** (Windows SecurityCenter2; stubs for macOS/Linux).
  - **Sleep/idle timeout** settings.
- Determines **issues automatically**:
  - `unencrypted_disk`
  - `outdated_os`
  - `no_antivirus`
  - `idle_sleep_too_high`
- Deduplicates reports using a **SHA-256 payload hash** to avoid duplicate submissions.
- Reports securely to the server using **API key authentication**.
- Lightweight daemon loop with randomized intervals.
- Stores data in **SQLite / any SQLAlchemy-compatible DB**.
- **Tables**:
  - `Machine` → static info (hostname, OS, architecture).
  - `Report` → dynamic health snapshots + issues.
- Endpoints:
  - `POST /ingest` → receive agent report (API key protected).
  - `GET /machines` → fetch latest machine states with:
    - Filters: OS, issues, hostname search (`q`).
    - Sorting: by hostname, OS, last check-in.
  - `GET /machines.csv` → export machine list to CSV with same filters.
- CORS enabled for dashboard.
- Frontend features:
  - **Filters**: by OS, issue type, hostname search.
  - **Sorting**: by name, OS, last check-in.
  - **CSV Export** with applied filters.
  - **Machine Table** with issues & status in real-time.
- Uses `fetch` + `axios` for API integration.

## Setup

Clone the repo and change the time for testing, currently it's between 15 to 60 minutes

### Backend (FastAPI)

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic
uvicorn app:app --reload --port 8000
```

will be visible at http://127.0.0.1:8000/machines

### Frontend (React)

```bash
cd dashboard
npm install
npm install axios
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm run dev
```

### Agent

```bash
cd agent
python -m venv .venv
.venv\Scripts\activate
pip install requests
python agent.py
```

#### Build Agent Executable

```bash
cd agent
python -m venv .venv
.venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile agent.py -n syshealth-agent
```

#### On windows, run installer:

```powershell
cd system_health_suite/agent/install/windows
.\install.ps1
```

### Manual Ingestion test

```powershell
cd system_health_suite
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ingest" -Method POST
  -Headers @{ "Content-Type" = "application/json"; "Authorization" = "Bearer DEV_AGENT_KEY" }`
  -Body '{ "machine_id": "test123", "hostname": "test-PC",
           "os": {"system": "Windows", "release": "10", "version": "22H2", "architecture": "x64"}, "checks": {"disk_encryption": true, "antivirus": true},
           "issues": {"unencrypted_disk": false, "outdated_os": false, "no_antivirus": false, "idle_sleep_too_high": true},
           "timestamp": "2025-08-16T12:45:00" }'
```
