# Codex Plugin Unlocker

Codex Plugin Unlocker is a minimal Windows launcher for Codex Desktop. It starts Codex with a Chromium DevTools Protocol port and injects a small renderer script that enables the plugin UI in API-key mode.

This project is a third-party local tool. It is not an OpenAI official release.

## Features

- Unlocks the Codex Desktop plugin sidebar entry in API-key mode.
- Enables disabled plugin install buttons caused by `App unavailable` / application unavailable frontend checks.
- Keeps the original sidebar label as `插件` / `Plugins`.
- Avoids session deletion, session movement, Markdown export, watcher takeover, and Codex database writes.
- Exits instead of killing existing Codex processes when Codex is already running without a debug port.

## Requirements

- Windows
- Codex Desktop
- Python 3.11+
- Node.js, used only by the install script for a JavaScript syntax check

## Quick Install

Clone the repository, then run:

```powershell
.\scripts\install.ps1
```

The installer creates a project-local `.venv`, installs the package, runs tests, checks the injected JavaScript syntax, and creates this desktop shortcut:

```text
Codex Plugin Unlocker.lnk
```

## Usage

1. Close any normal Codex Desktop window.
2. Launch Codex through `Codex Plugin Unlocker.lnk`.
3. Open the plugin page from the Codex sidebar.

If Codex is already running with debug port `9229`, the launcher injects into that existing debuggable window. If Codex is running without the debug port, the launcher exits and asks for Codex to be closed first.

## Manual Commands

```powershell
python -m codex_plugin_unlocker launch
python -m codex_plugin_unlocker install-shortcut
python -m codex_plugin_unlocker uninstall-shortcut
codex-plugin-unlocker launch
```

## Uninstall

```powershell
.\scripts\uninstall.ps1
```

The uninstall script removes the desktop shortcut and Windows uninstall entry. The repository directory and `.venv` remain available for inspection or manual deletion.

## Failure Log

Launcher failures are written to:

```text
%USERPROFILE%\.codex-plugin-unlocker\launcher.log
```

## Security Notes

The tool injects JavaScript into the local Codex Desktop renderer through Chromium DevTools Protocol. The injected script changes frontend state only. It does not patch Codex installation files, register a watcher, add a startup task, modify `state_5.sqlite`, or delete local conversation data.

The unlock relies on Codex Desktop frontend implementation details and may break after Codex updates.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
node --check codex_plugin_unlocker/inject/plugin-unlock.js
```
