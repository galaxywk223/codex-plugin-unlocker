$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvDir = Join-Path $ProjectRoot ".venv"
$Python = Join-Path $VenvDir "Scripts\python.exe"

if ($env:OS -ne "Windows_NT") {
    throw "Codex Plugin Unlocker 当前仅支持 Windows。"
}

$SystemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $SystemPython) {
    throw "PATH 中未找到 Python 3.11+。"
}

$versionText = & $SystemPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$versionText -lt [version]"3.11") {
    throw "需要 Python 3.11+，当前版本为 Python $versionText。"
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
Write-Host "Codex Plugin Unlocker 安装完成。"
Write-Host "桌面快捷方式：Codex Plugin Unlocker.lnk"
Write-Host "关闭普通 Codex 窗口后，通过新快捷方式启动 Codex。"
