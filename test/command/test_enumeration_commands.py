import os
import unittest
from unittest import mock

import commands.enumeration_commands as enumeration_commands
from test.fixture.dummy_context import DummyContextTest


class TestEnumerationCommands(DummyContextTest):
    def test_suid_uses_a_single_find_invocation(self):
        expected_command = (
            r"find / -perm -4000 -type f ! -path '/dev/*' -exec ls -la {} \; 2>/dev/null"
        )

        with mock.patch.object(
            enumeration_commands, "shell_exec"
        ) as shell_exec, mock.patch.object(enumeration_commands, "write_str"):
            enumeration_commands.Suid("!suid").execute()

        shell_exec.assert_called_once_with(expected_command, print_output=True)

    def test_dirwalk_writes_output_into_local_directory(self):
        with mock.patch.object(
            enumeration_commands.random, "choices", return_value=list("ABCDE")
        ):
            with mock.patch.object(
                enumeration_commands, "shell_exec", return_value="tree output"
            ):
                with mock.patch.object(enumeration_commands.os.path, "isdir", return_value=False):
                    with mock.patch.object(enumeration_commands.os, "mkdir") as mkdir:
                        with mock.patch("builtins.open", mock.mock_open()) as file_open:
                            cmd = enumeration_commands.DirWalk("!dirwalk", "/tmp/input")
                            cmd.execute()

        mkdir.assert_called_once_with("dirwalk")
        file_open.assert_called_once_with("dirwalk/ABCDE.txt", "w")

    def test_mtime_accepts_a_simple_positive_integer(self):
        with mock.patch.object(enumeration_commands, "shell_exec") as shell_exec:
            cmd = enumeration_commands.Mtime("!mtime", "5")
            cmd.execute()

        self.assertEqual(cmd.time, 5)
        shell_exec.assert_called_once_with(
            'find / -type f -mmin -5 ! -path "/proc/*" ! -path "/sys/*" ! -path "/run/*" ! -path "/dev/*" ! -path "/var/lib/*" 2>/dev/null',
            print_output=True,
        )

    def test_mtime_rejects_non_positive_input(self):
        with self.assertRaises(RuntimeError):
            enumeration_commands.Mtime("!mtime", "0")


if __name__ == "__main__":
    unittest.main()
