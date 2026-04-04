import types
import unittest
from unittest import mock

import model.driver.input_api as input_api


class TestInputAPI(unittest.TestCase):
    def test_file_exists_quotes_paths(self):
        with mock.patch.object(input_api, "shell_exec", return_value="0") as shell_exec:
            self.assertTrue(input_api.file_exists("/tmp/has space;echo nope"))
        shell_exec.assert_called_once_with(
            "test -f '/tmp/has space;echo nope' ; echo $?", timeout=30
        )

    def test_is_directory_quotes_paths(self):
        with mock.patch.object(input_api, "shell_exec", return_value="0") as shell_exec:
            self.assertTrue(input_api.is_directory("/tmp/dir with spaces"))
        shell_exec.assert_called_once_with(
            "test -d '/tmp/dir with spaces' ; echo $?", timeout=30
        )

    def test_read_all_output_uses_remaining_timeout(self):
        master = object()
        session = types.SimpleNamespace(
            master=master, input_driver=types.SimpleNamespace(last_line="PROMPT")
        )
        old_context = input_api.context
        old_time = getattr(input_api, "time", None)
        input_api.context = types.SimpleNamespace(active_session=session)
        input_api.time = types.SimpleNamespace(
            monotonic=mock.Mock(side_effect=[100.0, 101.0, 103.5, 106.0])
        )

        select_calls = []

        def fake_select(readable, writable, exceptional, timeout):
            select_calls.append(timeout)
            if len(select_calls) < 3:
                return ([master], [], [])
            return ([], [], [])

        try:
            with mock.patch.object(input_api.select, "select", side_effect=fake_select):
                with mock.patch.object(
                    input_api.os, "read", side_effect=[b"partial", b" output"]
                ):
                    with mock.patch.object(input_api, "write_str"):
                        result = input_api._read_all_output(5)
        finally:
            input_api.context = old_context
            if old_time is None:
                delattr(input_api, "time")
            else:
                input_api.time = old_time

        self.assertEqual(result, "partial output")
        self.assertEqual(select_calls, [4.0, 1.5])
