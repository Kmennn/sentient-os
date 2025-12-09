
# Enhanced Start Script for Sentient OS Offline
# Usage: .\start_offline.ps1 [-NoFlutter]

param(
    [switch]$NoFlutter
)

Write-Host "=== Sentient OS Shutdown/Startup Sequence ===" -ForegroundColor Cyan

# 1. Kill existing instances
Write-Host "Stopping existing instances..."
Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" } | Stop-Process -Force

# 2. Start Ollama
Write-Host "Starting Ollama..."
$ollama = Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -PassThru
if ($ollama.Id) {
    Write-Host "Ollama started (PID: $($ollama.Id))" -ForegroundColor Green
}
else {
    Write-Host "Failed to start Ollama. Is it installed?" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 3

# 0. Run DB Migration (v1.8)
Write-Host "Running DB Migration..."
$brainDir = Join-Path $PSScriptRoot "..\brain"
$venv = Join-Path $brainDir ".venv\Scripts\Activate.ps1"
$migCmd = "Set-Location '$brainDir'; & '$venv'; python scripts/migrate_db_v1_8.py"
Invoke-Expression $migCmd

# 3. Start Brain (Port 8000)
Write-Host "Starting Brain Service..."
$brainCmd = "Set-Location '$brainDir'; & '$venv'; uvicorn brain_server:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $brainCmd -WindowStyle Minimized

# 4. Start Body (Local Kernel - Port 8001)
Write-Host "Starting Body Service..."
$bodyDir = Join-Path $PSScriptRoot "..\local_kernel"
# Assuming body uses same venv for simplicity, or we can just use python if installed globally, 
# but best to use the same venv or a dedicated one. Let's use Brain's venv for now as they share deps mostly.
# If body has own deps, we should activate that. Assuming standard python usage.
$bodyCmd = "Set-Location '$bodyDir'; & '$venv'; uvicorn kernel:app --host 0.0.0.0 --port 8001 --reload"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $bodyCmd -WindowStyle Minimized

# 5. Start Flutter App
if (-not $NoFlutter) {
    Write-Host "Starting App..."
    $appDir = Join-Path $PSScriptRoot "..\hello_ai_os"
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location '$appDir'; flutter run -d windows" -WindowStyle Normal
}

Write-Host "All systems operational." -ForegroundColor Green
Write-Host "Brain running on http://localhost:8000"
