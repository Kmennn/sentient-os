# ONE-COMMAND SETUP & STARTER for Sentient OS v1.6 OFFLINE
# Run this whole block in Admin PowerShell. It will:
# 1) create branch, 2) setup venv & install deps, 3) start ollama (detached), 4) pull model,
# 5) set envs, 6) launch Brain in new terminal, 7) run verify script in new terminal.

# -- CONFIG (change only if your repo path is different) --
$RepoRoot = "C:\Users\Virendra\ai-os"
$BrainDir = Join-Path $RepoRoot "brain"
$HelloDir = Join-Path $RepoRoot "hello_ai_os"
$VenvActivate = Join-Path $BrainDir ".venv\Scripts\Activate.ps1"
$ModelName = "mistral"
$OllamaCmd = "ollama"            # assumes 'ollama' is on PATH
$OLLAMA_URL = "http://127.0.0.1:11434"

# -- 0) Create branch and pull latest (safe if already on branch) --
Push-Location $RepoRoot
if ((git rev-parse --abbrev-ref HEAD) -ne "feat/offline-intel-v1.6") {
  git checkout -b feat/offline-intel-v1.6 2>$null -Force
}
git pull origin main 2>$null
Pop-Location

# -- 1) Create & activate venv, install requirements (idempotent) --
if (-not (Test-Path -Path $VenvActivate)) {
  cd $BrainDir
  python -m venv .venv
}
# activate for this session and install deps
& powershell -NoProfile -Command "Set-Location -Path '$BrainDir'; & '$VenvActivate'; python -m pip install --upgrade pip; pip install -r requirements.txt"

# -- 2) Start Ollama (detached) if not already listening on 11434 --
$portLines = (netstat -ano | findstr ":11434") 2>$null
if (-not $portLines) {
  Write-Output "Starting Ollama (detached window)..."
  Start-Process -FilePath $OllamaCmd -ArgumentList "serve" -WindowStyle Normal
  Start-Sleep -Seconds 3
} else {
  Write-Output "Port 11434 already in use; assuming Ollama running."
}

# -- 3) Pull model if missing --
# (silent if model exists)
try {
  $models = & $OllamaCmd ls 2>$null
  if ($models -notmatch $ModelName) {
    Write-Output "Pulling model $ModelName (this may take time)..."
    & $OllamaCmd pull $ModelName
  } else {
    Write-Output "Model $ModelName already available."
  }
} catch {
  Write-Warning "Warning: unable to query ollama ls or pull; ensure Ollama is running and reachable on PATH. Error: $_"
}

# -- 4) Set environment variables for this session and persist them --
$env:OLLAMA_URL = $OLLAMA_URL
$env:OLLAMA_MODEL = $ModelName
setx OLLAMA_URL $OLLAMA_URL | Out-Null
setx OLLAMA_MODEL $ModelName | Out-Null
Write-Output "Environment variables set: OLLAMA_URL=$OLLAMA_URL, OLLAMA_MODEL=$ModelName"

# -- 5) Launch Brain in a new PowerShell window (keeps running) --
$brainCommand = @"
Set-Location -Path '$BrainDir'
& '$VenvActivate'
Write-Output 'Starting Brain (python main.py) in new window...'
python main.py
"@
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$brainCommand -WindowStyle Normal

# -- 6) Launch verification script in another new PowerShell window --
$verifyCommand = @"
Set-Location -Path '$RepoRoot'
Write-Output 'Running verify_offline.py...'
python .\tests\verify_offline.py
Write-Output 'verify_offline finished. Inspect output.'
"@
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$verifyCommand -WindowStyle Normal

# -- 7) Optional: start Flutter in Chrome (commented out; uncomment to use) --
# Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command","Set-Location -Path '$HelloDir'; flutter pub get; flutter run -d chrome" -WindowStyle Normal

Write-Output "`nDONE: Ollama (detached), Brain (new window), Verify (new window) started. Check windows for logs."
Write-Output "If anything fails, inspect each window: Ollama, Brain, Verify. Then paste any error text here for help."
