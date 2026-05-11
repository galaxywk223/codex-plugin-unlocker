$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvDir = Join-Path $ProjectRoot ".venv"
$Python = Join-Path $VenvDir "Scripts\python.exe"

if ($env:OS -ne "Windows_NT") {
    throw "Codex Plugin Unlocker currently supports Windows only."
}

$SystemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $SystemPython) {
    throw "Python 3.11+ was not found on PATH."
}

$versionText = & $SystemPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$versionText -lt [version]"3.11") {
    throw "Python 3.11+ is required. Found Python $versionText."
}

if (-not (Test-Path -LiteralPath $Python)) {
    & $SystemPython -m venv $VenvDir
}

& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -e ".[test]"
& $Python -m pytest -q
& node --check (Join-Path $ProjectRoot "codex_plugin_unlocker\inject\plugin-unlock.js")
& $Python -m codex_plugin_unlocker install-shortcut

Write-Host ""
Write-Host "Codex Plugin Unlocker installed."
Write-Host "Desktop shortcut: Codex Plugin Unlocker.lnk"
Write-Host "Close any normal Codex window, then launch Codex through the new shortcut."
