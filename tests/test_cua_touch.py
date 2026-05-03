"""Tests for cua_touch Python client."""
from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from cua_touch import CuAError, CuATouch, get_client


class TestCuATouchInit:
    """Test CuATouch initialization and binary discovery."""

    def test_init_with_explicit_binary(self):
        client = CuATouch(binary="/custom/bin/cua-driver", debug=True)
        assert client.binary == "/custom/bin/cua-driver"
        assert client.debug is True
        assert client._daemon_started is False

    def test_find_binary_falls_back_to_path(self):
        with patch("os.path.exists", return_value=False):
            with patch("shutil.which", return_value="cua-driver"):
                # Reset the binary to trigger path fallback
                client = CuATouch(binary="cua-driver")
                # When no candidates exist, raises CuAError
                with patch("os.path.exists", return_value=False):
                    try:
                        CuATouch(binary=None)
                    except CuAError:
                        pass

    def test_singleton_instance(self):
        client = CuATouch(binary="/dummy/cua-driver")
        assert CuATouch._instance is client


class TestCallRaw:
    """Test raw subprocess calls."""

    @patch("subprocess.run")
    def test_call_raw_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"windows": []}'
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        result = client._call_raw("list_windows", "{}")
        assert result == {"windows": []}
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_call_raw_nonzero_exit(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver", debug=True)
        result = client._call_raw("get_window_state", "{}")
        assert result is None

    @patch("subprocess.run")
    def test_call_raw_json_decode_error(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not json"
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        with pytest.raises(CuAError, match="Invalid JSON"):
            client._call_raw("get_window_state", "{}")


class TestListWindows:
    """Test list_windows method."""

    @patch("subprocess.run")
    def test_list_windows_all(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Main"},
                {"pid": 5678, "window_id": 2, "title": "Popup"},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        windows = client.list_windows()
        assert len(windows) == 2
        assert windows[0]["pid"] == 1234

    @patch("subprocess.run")
    def test_list_windows_filter_by_pid(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Main"},
                {"pid": 5678, "window_id": 2, "title": "Other"},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        windows = client.list_windows(pid=1234)
        assert len(windows) == 1
        assert windows[0]["pid"] == 1234


class TestFindPopupWindows:
    """Test find_popup_windows method."""

    @patch("subprocess.run")
    def test_find_popup_by_keyword(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Main Window"},
                {"pid": 1234, "window_id": 2, "title": "OAuth Popup"},
                {"pid": 1234, "window_id": 3, "title": "Consent Dialog"},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        popups = client.find_popup_windows(pid=1234, title_patterns=["popup", "consent"])
        assert len(popups) == 2

    @patch("subprocess.run")
    def test_find_popup_no_filter_returns_named_windows(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Main"},
                {"pid": 1234, "window_id": 2, "title": ""},
                {"pid": 1234, "window_id": 3, "title": "Popup"},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        popups = client.find_popup_windows(pid=1234)
        assert len(popups) == 2  # Main + Popup (not empty title)


class TestParseTreeMarkdown:
    """Test AX tree markdown parsing."""

    def test_parse_simple_elements(self):
        elements = CuATouch._parse_tree_markdown("""
- [0] Button "Submit"
- [1] TextField "Email"
- [2] StaticText "Welcome"
        """.strip())
        assert len(elements) == 3
        assert elements[0]["element_index"] == 0
        assert elements[0]["role"] == "Button"
        assert elements[0]["label"] == '"Submit"'

    def test_parse_elements_with_actions(self):
        elements = CuATouch._parse_tree_markdown("""
- [5] Button "Sign in" actions=press,click
- [10] AXLink "Learn more" actions=press
        """.strip())
        assert elements[0]["element_index"] == 5
        assert elements[0]["role"] == "Button"
        assert elements[0]["label"] == '"Sign in"'

    def test_parse_empty_tree(self):
        elements = CuATouch._parse_tree_markdown("")
        assert elements == []

    def test_parse_indented_elements(self):
        elements = CuATouch._parse_tree_markdown("""
  - [3] Group "Container"
    - [4] Button "Ok"
        """.strip())
        assert len(elements) == 2
        assert elements[1]["element_index"] == 4
        assert elements[1]["label"] == '"Ok"'


class TestGetWindowState:
    """Test get_window_state method."""

    @patch("subprocess.run")
    def test_get_window_state_parses_markdown(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "pid": 1234,
            "window_id": 99,
            "title": "OAuth",
            "tree_markdown": "- [25] Button \"Continue\"\n- [30] TextField \"Email\""
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        state = client.get_window_state(pid=1234, window_id=99)
        assert state["pid"] == 1234
        assert state["window_id"] == 99
        assert len(state["elements"]) == 2
        assert state["elements"][0]["element_index"] == 25


class TestClickAndSetValue:
    """Test click and set_value methods."""

    @patch("subprocess.run")
    def test_click(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        result = client.click(pid=1234, window_id=99, element_index=35)
        assert result["success"] is True
        call_args = mock_run.call_args[0][0]
        assert call_args[-2] == "click"
        params = json.loads(call_args[-1])
        assert params["element_index"] == 35
        assert params["action"] == "press"

    @patch("subprocess.run")
    def test_click_with_action(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        client.click(pid=1234, window_id=99, element_index=10, action="press")
        call_args = mock_run.call_args[0][0]
        params = json.loads(call_args[-1])
        assert params["action"] == "press"

    @patch("subprocess.run")
    def test_set_value(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        result = client.set_value(pid=1234, window_id=99, element_index=25, value="test@example.com")
        assert result["success"] is True
        call_args = mock_run.call_args[0][0]
        params = json.loads(call_args[-1])
        assert params["value"] == "test@example.com"
        assert params["element_index"] == 25


class TestWaitForElement:
    """Test wait_for_element method."""

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_wait_for_element_found(self, mock_run, mock_sleep):
        # First call returns no matching element, second returns it
        mock_result_1 = MagicMock()
        mock_result_1.returncode = 0
        mock_result_1.stdout = json.dumps({
            "tree_markdown": "- [1] Button \"Submit\""
        })

        mock_result_2 = MagicMock()
        mock_result_2.returncode = 0
        mock_result_2.stdout = json.dumps({
            "tree_markdown": "- [5] Button \"Continue\""
        })

        mock_run.side_effect = [mock_result_1, mock_result_2]

        client = CuATouch(binary="/dummy/cua-driver")
        idx = client.wait_for_element(pid=1234, window_id=99, element_label="Continue", timeout=2.0)
        assert idx == 5

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_wait_for_element_timeout(self, mock_run, mock_sleep):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "tree_markdown": "- [1] Button \"Submit\""
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        idx = client.wait_for_element(pid=1234, window_id=99, element_label="NonExistent", timeout=0.2)
        assert idx is None


class TestAutoDetectPopup:
    """Test auto_detect_popup method."""

    @patch("subprocess.run")
    def test_auto_detect_by_keyword(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Chrome", "bounds": {}},
                {"pid": 1234, "window_id": 2, "title": "Sign in - Google", "bounds": {}},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        popup = client.auto_detect_popup(pid=1234)
        assert popup is not None
        assert "Google" in popup["title"]

    @patch("subprocess.run")
    def test_auto_detect_by_size(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "windows": [
                {"pid": 1234, "window_id": 1, "title": "Chrome", "bounds": {"width": 1920, "height": 1080}},
                {"pid": 1234, "window_id": 2, "title": "Dialog", "bounds": {"width": 400, "height": 300}},
            ]
        })
        mock_run.return_value = mock_result

        client = CuATouch(binary="/dummy/cua-driver")
        popup = client.auto_detect_popup(pid=1234, keywords=["nonexistent"])
        assert popup is not None
        assert popup["window_id"] == 2


class TestGetClient:
    """Test singleton get_client() factory."""

    def test_get_client_creates_instance(self):
        # Reset singleton
        CuATouch._instance = None
        with patch.object(CuATouch, "connect", return_value=True):
            with patch.object(CuATouch, "_find_binary", return_value="/dummy/cua-driver"):
                client = get_client()
                assert client is not None
        # Reset for other tests
        CuATouch._instance = None