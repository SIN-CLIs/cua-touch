"""cua_touch — Python client for cua-driver daemon.

Usage:
    from cua_touch import CuATouch
    c = CuATouch()
    c.connect()
    windows = c.list_windows(pid=3436)
    state = c.get_window_state(pid=3436, window_id=36438)
    c.click(pid=3436, window_id=36438, element_index=35)
    c.set_value(pid=3436, window_id=36438, element_index=25, value="email@gmail.com")
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import time
from typing import Any

DAEMON_PORT = 9876
DAEMON_STARTUP_TIMEOUT = 5
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 0.5


class CuAError(Exception):
    pass


class CuATouch:
    _instance = None

    def __init__(self, binary: str | None = None, debug: bool = False):
        self.binary = binary or self._find_binary()
        self.debug = debug
        self._daemon_started = False
        CuATouch._instance = self

    @staticmethod
    def _find_binary() -> str:
        for candidate in [
            "/Applications/CuaDriver.app/Contents/MacOS/cua-driver",
            "/usr/local/bin/cua-driver",
            "/usr/bin/cua-driver",
            "cua-driver",
        ]:
            if os.path.exists(candidate):
                return candidate
        raise CuAError("cua-driver binary not found")

    def connect(self, retries: int = DEFAULT_RETRY_COUNT) -> bool:
        for attempt in range(retries):
            try:
                result = self._call_raw("list_windows", "{}")
                if result is not None:
                    return True
            except CuAError:
                pass
            if attempt == 0:
                self._start_daemon()
            time.sleep(DEFAULT_RETRY_DELAY)
        raise CuAError("Failed to connect to cua-driver daemon")

    def _start_daemon(self) -> None:
        if self._daemon_started:
            return
        try:
            subprocess.run(
                [self.binary, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
        except Exception:
            pass
        self._daemon_started = True
        time.sleep(1)

    def _call_raw(self, method: str, params_json: str) -> dict[str, Any] | None:
        try:
            result = subprocess.run(
                [self.binary, "call", method, params_json],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                if self.debug:
                    print(f"[cua-touch] {method} failed: {result.stderr}")
                return None
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise CuAError(f"Timeout calling {method}")
        except json.JSONDecodeError:
            raise CuAError(f"Invalid JSON from {method}: {result.stdout[:200]}")

    def _call(self, method: str, params: dict[str, Any],
              retries: int = DEFAULT_RETRY_COUNT) -> dict[str, Any]:
        params_json = json.dumps(params)
        last_error = None
        for attempt in range(retries):
            result = self._call_raw(method, params_json)
            if result is not None:
                return result
            last_error = CuAError(f"{method} returned no data (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                time.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
        raise last_error or CuAError(f"{method} failed after {retries} attempts")

    def list_windows(self, pid: int | None = None) -> list[dict[str, Any]]:
        result = self._call("list_windows", {})
        windows = result.get("windows", [])
        if pid is not None:
            windows = [w for w in windows if w.get("pid") == pid]
        return windows

    def find_popup_windows(self, pid: int,
                           title_patterns: list[str] | None = None) -> list[dict[str, Any]]:
        windows = self.list_windows(pid=pid)
        if not title_patterns:
            return [w for w in windows if w.get("title") not in ("", None)]
        matched = []
        for w in windows:
            title = w.get("title", "")
            for pattern in title_patterns:
                if pattern.lower() in title.lower():
                    matched.append(w)
                    break
        return matched

    def get_window_state(self, pid: int, window_id: int,
                         retries: int = DEFAULT_RETRY_COUNT) -> dict[str, Any]:
        result = self._call("get_window_state", {"pid": pid, "window_id": window_id}, retries)
        tree_md = result.get("tree_markdown", "")
        result["elements"] = self._parse_tree_markdown(tree_md)
        return result

    @staticmethod
    def _parse_tree_markdown(tree_md: str) -> list[dict[str, Any]]:
        elements = []
        for line in tree_md.splitlines():
            m = re.match(r"\s*-\s*\[(\d+)\]\s+(\w+)\s*(.*)", line)
            if m:
                idx = int(m.group(1))
                role = m.group(2)
                rest = m.group(3).strip()
                label_match = re.match(r"(.*?)\s+actions=", rest)
                label = label_match.group(1).strip() if label_match else rest.strip()
                elements.append({"element_index": idx, "role": role, "label": label})
        return elements

    def click(self, pid: int, window_id: int, element_index: int,
              action: str = "press", retries: int = DEFAULT_RETRY_COUNT) -> dict[str, Any]:
        return self._call("click", {
            "pid": pid,
            "window_id": window_id,
            "element_index": element_index,
            "action": action,
        }, retries)

    def set_value(self, pid: int, window_id: int, element_index: int,
                  value: str, retries: int = DEFAULT_RETRY_COUNT) -> dict[str, Any]:
        return self._call("set_value", {
            "pid": pid,
            "window_id": window_id,
            "element_index": element_index,
            "value": value,
        }, retries)

    def wait_for_element(self, pid: int, window_id: int,
                         element_label: str, timeout: float = 10.0) -> int | None:
        start = time.time()
        while time.time() - start < timeout:
            state = self.get_window_state(pid, window_id)
            elements = state.get("elements", [])
            for elem in elements:
                label = elem.get("label", "")
                if element_label.lower() in label.lower():
                    return elem.get("element_index")
            time.sleep(0.5)
        return None

    def auto_detect_popup(self, pid: int,
                          keywords: list[str] | None = None) -> dict[str, Any] | None:
        keywords = keywords or ["popup", "consent", "google", "oauth", "dialog", "popup"]
        windows = self.list_windows(pid=pid)
        for w in windows:
            title = w.get("title", "").lower()
            if any(kw in title for kw in keywords):
                return w
        for w in windows:
            title = w.get("title", "")
            if title and title not in ("", "Chrome", "Google Chrome"):
                bounds = w.get("bounds", {})
                if bounds.get("width", 0) < 800:
                    return w
        return None


def get_client() -> CuATouch:
    if CuATouch._instance is None:
        CuATouch._instance = CuATouch()
        CuATouch._instance.connect()
    return CuATouch._instance