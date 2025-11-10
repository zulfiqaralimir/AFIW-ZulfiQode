@echo off
echo ============================================================
echo        Starting AFIW–ZulfiQode: Lawyer-AI Local Stack
echo ============================================================

REM === 1️⃣ Start FastAPI Backend (Lawyer-AI Core) ===
echo [1/6] Starting FastAPI backend on port 8001...
start cmd /k "cd /d D:\AFIW_ZulfiQode_Final && venv\Scripts\activate && uvicorn app.main:app --port 8001"
timeout /t 5 >nul

REM === 2️⃣ Start Streamlit Dashboard ===
echo [2/6] Starting Streamlit dashboard on port 8000...
start cmd /k "cd /d D:\AFIW_ZulfiQode_Final && venv\Scripts\activate && streamlit run streamlit_app\dashboard_lawyer_ai.py --server.port 8000"
timeout /t 5 >nul

REM === 3️⃣ Start Prometheus (Metrics Collector) ===
echo [3/6] Starting Prometheus monitoring service...
start cmd /k "C:\prometheus\prometheus.exe --config.file=D:\AFIW_ZulfiQode_Final\prometheus\prometheus.yml"
timeout /t 5 >nul

REM === 4️⃣ Start Grafana (Check if already running first) ===
echo [4/6] Checking Grafana status...
tasklist /FI "IMAGENAME eq grafana-server.exe" | find /I "grafana-server.exe" >nul
if %errorlevel%==0 (
    echo Grafana is already running, skipping startup...
) else (
    echo Starting Grafana visualization dashboard...
    cd /d "C:\Program Files\GrafanaLabs\grafana\bin"
    start cmd /k "grafana-server.exe"
    echo Waiting for Grafana to initialize...
    timeout /t 15 >nul
)

REM === 5️⃣ Automatically Import Grafana Dashboard via API ===
echo [5/6] Importing Lawyer-AI dashboard into Grafana (auto)...
powershell -Command ^
  "$json = Get-Content 'D:\AFIW_ZulfiQode_Final\grafana\LawyerAI_Dashboard.json' -Raw; ^
  try { Invoke-RestMethod -Uri 'http://admin:admin@localhost:3000/api/dashboards/db' -Method Post -Body $json -ContentType 'application/json'; ^
  Write-Host '✅ Dashboard imported successfully into Grafana.' } ^
  catch { Write-Host '⚠️ Grafana not ready yet. Try re-running after it starts.' }"

REM === 6️⃣ Open Browser Dashboards ===
echo [6/6] Opening dashboards in browser...
start http://localhost:8000
start http://127.0.0.1:8001/docs
start http://localhost:9090/targets
start http://localhost:3000

echo ============================================================
echo All Lawyer-AI services are now running locally ✅
echo ------------------------------------------------------------
echo  FastAPI (API):      http://127.0.0.1:8001
echo  Streamlit (UI):     http://localhost:8000
echo  Prometheus:         http://localhost:9090
echo  Grafana:            http://localhost:3000
echo ============================================================
pause
