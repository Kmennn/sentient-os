# Sentient OS Launcher
Write-Host "Starting Sentient OS Backend..."
Start-Process python -ArgumentList "brain/main.py" -WorkingDirectory "C:\Users\Virendra\ai-os"

Write-Host "Starting Sentient OS Frontend (Flutter)..."
Set-Location "hello_ai_os"
flutter run -d windows
