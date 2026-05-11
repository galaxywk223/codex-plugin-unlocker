from pathlib import Path

import pytest

from codex_plugin_unlocker import launcher


def test_existing_codex_without_debug_port_is_not_killed(monkeypatch):
    monkeypatch.setattr(launcher, "can_connect", lambda port: False)
    monkeypatch.setattr(launcher, "codex_process_ids", lambda: [123, 456])
    killed = []
    monkeypatch.setattr(launcher, "launch_codex", lambda *args: killed.append(args))

    with pytest.raises(RuntimeError, match="Close Codex first"):
        launcher.launch_and_inject(None, 9229)

    assert killed == []


def test_existing_debuggable_codex_gets_injected(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(launcher, "can_connect", lambda port: True)
    monkeypatch.setattr(launcher, "inject_file", lambda port, script_path: calls.append((port, script_path)))

    assert launcher.launch_and_inject(None, 9229) == 0
    assert calls
    assert calls[0][0] == 9229
    assert calls[0][1].name == "plugin-unlock.js"


def test_launch_path_resolves_and_injects(monkeypatch, tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    calls = []
    monkeypatch.setattr(launcher, "can_connect", lambda port: False)
    monkeypatch.setattr(launcher, "codex_process_ids", lambda: [])
    monkeypatch.setattr(launcher, "find_latest_codex_app_dir", lambda: app)
    monkeypatch.setattr(launcher, "launch_codex", lambda app_dir, debug_port: calls.append(("launch", app_dir, debug_port)))
    monkeypatch.setattr(launcher, "wait_for_debug_port", lambda port: calls.append(("wait", port)))
    monkeypatch.setattr(launcher, "inject_file", lambda port, script_path: calls.append(("inject", port, Path(script_path).name)))

    assert launcher.launch_and_inject(None, 9229) == 0
    assert calls == [("launch", app, 9229), ("wait", 9229), ("inject", 9229, "plugin-unlock.js")]
