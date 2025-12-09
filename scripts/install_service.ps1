
# Install Sentient OS as a Windows Service
# Requires 'nssm' (Non-Sucking Service Manager) to be on PATH or provided.
# If NSSM is not found, we advise user.

param(
    [string]$ServiceName = "SentientBrain"
)


if (-not (Get-Command "nssm" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: 'nssm' is not found in PATH." -ForegroundColor Red
    Write-Host "Please install NSSM (e.g., 'choco install nssm') or place nssm.exe in scripts folder."
    exit 1
}

$BrainDir = Join-Path $PSScriptRoot "..\brain"
$VenvPython = Join-Path $BrainDir ".venv\Scripts\python.exe"
$MainPy = Join-Path $BrainDir "main.py"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual Environment Python not found at: $VenvPython" -ForegroundColor Yellow
    Write-Host "Assuming global python or manual setup needed. Trying 'python' from PATH."
    $VenvPython = "python"
}

# Check if service exists
if (Get-Service $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Service $ServiceName already exists. Stopping and removing..."
    nssm stop $ServiceName
    nssm remove $ServiceName confirm
}

Write-Host "Installing Service: $ServiceName"
# Install
nssm install $ServiceName $VenvPython $MainPy
nssm set $ServiceName AppDirectory $BrainDir
nssm set $ServiceName AppStdout (Join-Path $BrainDir "service.log")
nssm set $ServiceName AppStderr (Join-Path $BrainDir "service_err.log")
nssm set $ServiceName Start SERVICE_AUTO_START
nssm set $ServiceName AppEnvironmentExtra "PYTHONUNBUFFERED=1"

Write-Host "Service installed. Starting..."
nssm start $ServiceName

Write-Host "Done. Check service.log for output." -ForegroundColor Green
Get-Service $ServiceName | Select-Object Status, Name, DisplayName

