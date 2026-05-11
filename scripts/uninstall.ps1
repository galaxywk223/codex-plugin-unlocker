$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (Test-Path -LiteralPath $Python) {
    & $Python -m codex_plugin_unlocker uninstall-shortcut
} else {
    $Desktop = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $Desktop "Codex Plugin Unlocker.lnk"
    if (Test-Path -LiteralPath $ShortcutPath) {
        Remove-Item -LiteralPath $ShortcutPath -Force
    }
    $UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\CodexPluginUnlocker"
    if (Test-Path $UninstallKey) {
        Remove-Item $UninstallKey -Force
    }
}

Write-Host "Codex Plugin Unlocker shortcut and uninstall entry removed."
