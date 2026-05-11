from __future__ import annotations

import ctypes
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from codex_plugin_unlocker.app_paths import find_latest_codex_app_dir
from codex_plugin_unlocker.cdp import inject_file, list_targets


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, value: str):
        parsed = uuid.UUID(value)
        data4 = bytes([parsed.clock_seq_hi_variant, parsed.clock_seq_low]) + parsed.node.to_bytes(6, "big")
        super().__init__(parsed.time_low, parsed.time_mid, parsed.time_hi_version, (ctypes.c_ubyte * 8)(*data4))


def can_connect(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


def codex_process_ids() -> list[int]:
    if sys.platform != "win32":
        return []
    command = (
        "Get-CimInstance Win32_Process -Filter \"Name='Codex.exe' OR Name='codex.exe'\" | "
        "Select-Object -ExpandProperty ProcessId"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    ids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def build_codex_arguments(debug_port: int) -> list[str]:
    return [
        f"--remote-debugging-port={debug_port}",
        f"--remote-allow-origins=http://127.0.0.1:{debug_port}",
    ]


def packaged_app_user_model_id(app_dir: Path) -> str | None:
    package_dir = app_dir.parent if app_dir.name.lower() == "app" else app_dir
    if not package_dir.name.startswith("OpenAI.Codex_") or "__" not in package_dir.name:
        return None
    identity_name = package_dir.name.split("_", 1)[0]
    publisher_id = package_dir.name.rsplit("__", 1)[1]
    if not publisher_id:
        return None
    return f"{identity_name}_{publisher_id}!App"


def _raise_for_hresult(hr: int, operation: str) -> None:
    if hr < 0:
        raise OSError(f"{operation} failed with HRESULT 0x{hr & 0xFFFFFFFF:08X}")


def activate_packaged_app(app_user_model_id: str, arguments: str) -> int:
    if sys.platform != "win32":
        raise RuntimeError("Packaged app activation is only supported on Windows")

    ole32 = ctypes.OleDLL("ole32")
    ole32.CoInitializeEx.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    ole32.CoInitializeEx.restype = ctypes.c_long
    ole32.CoUninitialize.argtypes = []
    ole32.CoUninitialize.restype = None
    ole32.CoCreateInstance.argtypes = [
        ctypes.POINTER(_GUID),
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(_GUID),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    ole32.CoCreateInstance.restype = ctypes.c_long

    coinit_hr = ole32.CoInitializeEx(None, 2)
    should_uninitialize = coinit_hr >= 0
    if coinit_hr < 0 and coinit_hr != -2147417850:  # RPC_E_CHANGED_MODE
        _raise_for_hresult(coinit_hr, "CoInitializeEx")

    activation_manager = ctypes.c_void_p()
    try:
        clsid = _GUID("45BA127D-10A8-46EA-8AB7-56EA9078943C")
        iid = _GUID("2e941141-7f97-4756-ba1d-9decde894a3d")
        _raise_for_hresult(
            ole32.CoCreateInstance(ctypes.byref(clsid), None, 1, ctypes.byref(iid), ctypes.byref(activation_manager)),
            "CoCreateInstance(ApplicationActivationManager)",
        )

        activate_application_type = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
        )
        vtable = ctypes.cast(activation_manager, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        activate_application = activate_application_type(vtable[3])
        process_id = ctypes.c_ulong()
        _raise_for_hresult(
            activate_application(activation_manager, app_user_model_id, arguments, 0, ctypes.byref(process_id)),
            "ActivateApplication",
        )
        return int(process_id.value)
    finally:
        if activation_manager.value:
            release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(
                ctypes.cast(activation_manager, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents[2]
            )
            release(activation_manager)
        if should_uninitialize:
            ole32.CoUninitialize()


def launch_codex(app_dir: Path, debug_port: int) -> Any:
    app_user_model_id = packaged_app_user_model_id(app_dir) if sys.platform == "win32" else None
    if app_user_model_id:
        return activate_packaged_app(app_user_model_id, subprocess.list2cmdline(build_codex_arguments(debug_port)))
    executable = app_dir / "Codex.exe"
    return subprocess.Popen([str(executable), *build_codex_arguments(debug_port)])


def wait_for_debug_port(port: int, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            list_targets(port)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Codex debug port did not become ready on {port}: {last_error}")


def launch_and_inject(app_dir: Path | None, debug_port: int, attach_existing: bool = False) -> int:
    script_path = Path(__file__).parent / "inject" / "plugin-unlock.js"
    if can_connect(debug_port):
        inject_file(debug_port, script_path)
        return 0

    running_pids = codex_process_ids()
    if running_pids and not attach_existing:
        joined = ", ".join(str(pid) for pid in running_pids)
        raise RuntimeError(
            "Codex is already running without the debug port. "
            f"Close Codex first, then launch through Codex Plugin Unlocker. Running PIDs: {joined}"
        )

    resolved_app_dir = app_dir or find_latest_codex_app_dir()
    if resolved_app_dir is None:
        raise RuntimeError("Codex App directory not found")

    launch_codex(resolved_app_dir, debug_port)
    wait_for_debug_port(debug_port)
    inject_file(debug_port, script_path)
    return 0
