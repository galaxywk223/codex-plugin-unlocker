from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from codex_plugin_unlocker import __version__


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def default_install_root() -> Path:
    return Path.home() / "Desktop"


def install_shortcut(install_root: Path | None = None) -> None:
    if sys.platform != "win32":
        raise RuntimeError("Shortcut installation is only supported on Windows")
    root = install_root or default_install_root()
    project_root = Path(__file__).resolve().parent.parent
    python = Path(sys.executable)
    pythonw = python.with_name("pythonw.exe")
    target = pythonw if pythonw.exists() else python
    script = f"""
$InstallRoot = {_ps_quote(str(root))}
$ProjectRoot = {_ps_quote(str(project_root))}
$Target = {_ps_quote(str(target))}
$Arguments = '-m codex_plugin_unlocker launch'
New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
$ShortcutPath = Join-Path $InstallRoot 'Codex Plugin Unlocker.lnk'
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = 'Launch Codex with plugin unlock injection'
$Shortcut.Save()
$UninstallKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CodexPluginUnlocker'
$UninstallCommand = 'cmd.exe /c cd /d "' + $ProjectRoot + '" && "' + {_ps_quote(str(python))} + '" -m codex_plugin_unlocker uninstall-shortcut --install-root "' + $InstallRoot + '"'
New-Item -Path $UninstallKey -Force | Out-Null
Set-ItemProperty -Path $UninstallKey -Name DisplayName -Value 'Codex Plugin Unlocker'
Set-ItemProperty -Path $UninstallKey -Name DisplayVersion -Value '{__version__}'
Set-ItemProperty -Path $UninstallKey -Name Publisher -Value 'Local'
Set-ItemProperty -Path $UninstallKey -Name InstallLocation -Value $ProjectRoot
Set-ItemProperty -Path $UninstallKey -Name UninstallString -Value $UninstallCommand
Set-ItemProperty -Path $UninstallKey -Name QuietUninstallString -Value $UninstallCommand
""".strip()
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True)


def uninstall_shortcut(install_root: Path | None = None) -> None:
    if sys.platform != "win32":
        return
    root = install_root or default_install_root()
    script = f"""
$InstallRoot = {_ps_quote(str(root))}
$ShortcutPath = Join-Path $InstallRoot 'Codex Plugin Unlocker.lnk'
if (Test-Path $ShortcutPath) {{ Remove-Item $ShortcutPath -Force }}
$UninstallKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CodexPluginUnlocker'
if (Test-Path $UninstallKey) {{ Remove-Item $UninstallKey -Force }}
""".strip()
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True)
