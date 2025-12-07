
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

# 3. Start Brain
Write-Host "Starting Brain..."
$brainDir = Join-Path $PSScriptRoot "..\brain"
$venv = Join-Path $brainDir ".venv\Scripts\Activate.ps1"

# We use a new window for Brain logs, but minimized/no focus if possible, 
# or just a standard window so user can see logs.
$brainCmd = "Set-Location '$brainDir'; & '$venv'; python main.py"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $brainCmd -WindowStyle Normal

# 4. Start Flutter (optional)
if (-not $NoFlutter) {
    Write-Host "Starting App..."
    $appDir = Join-Path $PSScriptRoot "..\hello_ai_os"
    # Assuming 'flutter run -d windows' or similar. 
    # For dev, we might just open the dir or run it.
    # Let's run in chrome for compatibility in this logic, or windows if available.
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location '$appDir'; flutter run -d windows" -WindowStyle Normal
}

Write-Host "All systems operational." -ForegroundColor Green
Write-Host "Brain running on http://localhost:8000"
