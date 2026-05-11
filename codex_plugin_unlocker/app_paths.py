from __future__ import annotations

import re
import subprocess
from pathlib import Path


_VERSION_RE = re.compile(r"OpenAI\.Codex_([0-9.]+)_")


def _version_tuple(path: Path) -> tuple[int, ...]:
    match = _VERSION_RE.search(path.name)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split(".") if part.isdigit())


def find_latest_codex_app_dir(root: Path | None = None) -> Path | None:
    if root is not None:
        matches = [path for path in root.iterdir() if path.is_dir() and _version_tuple(path)]
        if not matches:
            return None
        latest = max(matches, key=_version_tuple)
        app = latest / "app"
        return app if app.is_dir() else latest

    command = 'Get-AppxPackage -Name "OpenAI.Codex" | Select-Object -ExpandProperty InstallLocation'
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    root_path = Path(result.stdout.strip())
    app = root_path / "app"
    return app if app.is_dir() else root_path
