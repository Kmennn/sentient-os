
# Install Sentient OS as a Windows Service
# Requires 'nssm' (Non-Sucking Service Manager) to be on PATH or provided.
# If NSSM is not found, we advise user.

param(
    [string]$ServiceName = "SentientBrain"
)

if (-not (Get-Command "nssm" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: 'nssm' is not found in PATH." -ForegroundColor Red
    Write-Host "Please install NSSM (e.g., 'choco install nssm') to run as a service."
    Write-Host "Alternatively, use start_offline.ps1 for manual startup."
    exit 1
}

$BrainDir = Join-Path $PSScriptRoot "..\brain"
$VenvPython = Join-Path $BrainDir ".venv\Scripts\python.exe"
$MainPy = Join-Path $BrainDir "main.py"

Write-Host "Installing Service: $ServiceName"
Write-Host "Python: $VenvPython"
Write-Host "Script: $MainPy"

# Install
nssm install $ServiceName $VenvPython $MainPy
nssm set $ServiceName AppDirectory $BrainDir
nssm set $ServiceName AppStdout (Join-Path $BrainDir "service.log")
nssm set $ServiceName AppStderr (Join-Path $BrainDir "service_err.log")
nssm set $ServiceName Start SERVICE_AUTO_START

Write-Host "Service installed. Starting..."
nssm start $ServiceName

Write-Host "Done. Check service.log for output." -ForegroundColor Green
