from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from codex_plugin_unlocker.installer import install_shortcut, uninstall_shortcut
from codex_plugin_unlocker.launcher import launch_and_inject


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal Codex Desktop plugin unlock launcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    launch = subparsers.add_parser("launch", help="Launch Codex and inject plugin unlock script")
    launch.add_argument("--app-dir", type=Path, default=None)
    launch.add_argument("--debug-port", type=int, default=9229)
    launch.add_argument("--attach-existing", action="store_true", help="Inject into an already-debuggable Codex instance")

    install = subparsers.add_parser("install-shortcut", help="Create the desktop shortcut and uninstall entry")
    install.add_argument("--install-root", type=Path, default=None)

    uninstall = subparsers.add_parser("uninstall-shortcut", help="Remove the desktop shortcut and uninstall entry")
    uninstall.add_argument("--install-root", type=Path, default=None)

    return parser


def log_failure(exc: BaseException) -> None:
    log_path = Path.home() / ".codex-plugin-unlocker" / "launcher.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        if args.command == "launch":
            return launch_and_inject(args.app_dir, args.debug_port, attach_existing=args.attach_existing)
        if args.command == "install-shortcut":
            install_shortcut(args.install_root)
            return 0
        if args.command == "uninstall-shortcut":
            uninstall_shortcut(args.install_root)
            return 0
        raise RuntimeError(f"Unknown command: {args.command}")
    except Exception as exc:
        log_failure(exc)
        print(f"Codex Plugin Unlocker failed: {exc}", file=sys.stderr)
        return 1
