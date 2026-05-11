from __future__ import annotations

import json
from pathlib import Path

import requests
import websocket


def list_targets(port: int) -> list[dict[str, object]]:
    session = requests.Session()
    session.trust_env = False
    response = session.get(f"http://127.0.0.1:{port}/json", timeout=3)
    response.raise_for_status()
    return response.json()


def pick_page_target(targets: list[dict[str, object]]) -> dict[str, object]:
    pages = [target for target in targets if target.get("type") == "page" and target.get("webSocketDebuggerUrl")]
    for target in pages:
        title = str(target.get("title", ""))
        url = str(target.get("url", ""))
        if "codex" in (title + " " + url).lower():
            return target
    if pages:
        return pages[0]
    raise RuntimeError("No injectable Codex page target found")


def evaluate_script(websocket_url: str, script: str) -> dict[str, object]:
    ws = websocket.create_connection(websocket_url, timeout=5)
    try:
        payload = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": script,
                "awaitPromise": False,
                "allowUnsafeEvalBlockedByCSP": True,
            },
        }
        ws.send(json.dumps(payload))
        while True:
            message = json.loads(ws.recv())
            if message.get("id") == 1:
                if "error" in message:
                    raise RuntimeError(str(message["error"]))
                return message
    finally:
        ws.close()


def add_script_to_new_documents(websocket_url: str, script: str) -> dict[str, object]:
    ws = websocket.create_connection(websocket_url, timeout=5)
    try:
        payload = {
            "id": 1,
            "method": "Page.addScriptToEvaluateOnNewDocument",
            "params": {"source": script},
        }
        ws.send(json.dumps(payload))
        while True:
            message = json.loads(ws.recv())
            if message.get("id") == 1:
                if "error" in message:
                    raise RuntimeError(str(message["error"]))
                return message
    finally:
        ws.close()


def inject_file(port: int, script_path: Path) -> dict[str, object]:
    target = pick_page_target(list_targets(port))
    websocket_url = str(target["webSocketDebuggerUrl"])
    script = script_path.read_text(encoding="utf-8")
    add_script_to_new_documents(websocket_url, script)
    return evaluate_script(websocket_url, script)
