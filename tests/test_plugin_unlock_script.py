from pathlib import Path
import subprocess


SCRIPT = Path("codex_plugin_unlocker/inject/plugin-unlock.js")


def test_script_parses_with_node():
    result = subprocess.run(["node", "--check", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_script_keeps_both_unlock_features():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "function enablePluginEntry" in text
    assert "function unblockPluginInstallButtons" in text
    assert "setAuthMethod(\"chatgpt\")" in text
    assert "nav[role=\"navigation\"] button.h-token-nav-row.w-full" in text
    assert "svg path[d^=\"M7.94562 14.0277\"]" in text
    assert "button:disabled.w-full.justify-center" in text
    assert "[role=\"button\"][aria-disabled=\"true\"].cursor-not-allowed" in text
    assert "Plugins - Unlocked" not in text
    assert "插件 - 已解锁" not in text
    assert "normalizePluginEntryLabel" in text
    assert "强制安装" in text
    assert "removeAttribute(\"aria-disabled\")" in text


def test_script_excludes_codex_plus_session_features():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "/delete" not in text
    assert "/undo" not in text
    assert "export-markdown" not in text
    assert "move-thread-workspace" not in text
    assert "codex-delete-button" not in text
