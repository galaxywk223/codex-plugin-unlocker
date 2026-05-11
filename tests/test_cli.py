from pathlib import Path

from codex_plugin_unlocker import cli


def test_cli_logs_launch_failure(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    assert cli.main(["launch"]) == 1
    assert "boom" in (tmp_path / ".codex-plugin-unlocker" / "launcher.log").read_text(encoding="utf-8")
    assert "Codex Plugin Unlocker failed: boom" in capsys.readouterr().err
