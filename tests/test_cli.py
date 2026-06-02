from pathlib import Path

from codex_plugin_unlocker import cli


def test_cli_logs_launch_failure(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    assert cli.main(["launch"]) == 1
    assert "boom" in (tmp_path / ".codex-plugin-unlocker" / "launcher.log").read_text(encoding="utf-8")
    assert "Codex Plugin Unlocker failed: boom" in capsys.readouterr().err


def test_cli_shows_dialog_for_pythonw_launch_failure(monkeypatch, tmp_path):
    messages = []
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(cli, "should_show_failure_dialog", lambda: True)
    monkeypatch.setattr(cli, "show_failure_dialog", messages.append)

    assert cli.main(["launch"]) == 1
    assert len(messages) == 1
    assert "Codex Plugin Unlocker failed:" in messages[0]
    assert "boom" in messages[0]
    assert str(tmp_path / ".codex-plugin-unlocker" / "launcher.log") in messages[0]
