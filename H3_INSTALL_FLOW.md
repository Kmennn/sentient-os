# H3 Install Flow

## 1. Prerequisites

- **Brain**: Sentient Core configured and running on `localhost:8000`.
- **Runtime**: Flutter installed (`flutter doctor`).

## 2. Installation Steps

### A. Build the App

```bash
cd hello_ai_os
flutter build windows --release
# Output: build/windows/runner/Release/hello_ai_os.exe
```

### B. Configure Startup

1. Move `.exe` to `%APPDATA%\Sentient`.
2. Create Shortcut in `shell:startup`.
3. Set flag `--minimized` to start in tray.

### C. First Run Experience

1. **Launch**: App starts silently in tray.
2. **Onboarding**: Clicking the icon shows "Connecting to Brain...".
3. **Permission**: Requests Notification Access.
4. **Ready**: Shows "Shield Down. System Nominal."

## 3. Deployment Strategy

- **Distribution**: Single Binary + Assets.
- **Updates**: `git pull` -> Rebuild (No OTA yet).
- **Uninstall**: Delete folder (No registry keys).

## 4. Troubleshooting

- **White Screen**: Check if Brain API is reachable.
- **No Icon**: Ensure `windows/runner/resources/app_icon.ico` exists.
- **Crash**: Check `%TEMP%\sentient_logs.txt`.
