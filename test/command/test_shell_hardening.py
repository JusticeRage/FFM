import os
import tempfile
import types
import unittest
from unittest import mock

import commands.enumeration_commands as enumeration_commands
import commands.notty_sudo as notty_sudo
import commands.remote_script as remote_script
import commands.stealth_commands as stealth_commands
from model.driver.input_api import shell_quote
from test.fixture.dummy_context import DummyContextTest


class TestRemoteScriptHardening(DummyContextTest):
    def test_python3_script_quotes_arguments(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write("print('hello')\n")
            script_path = handle.name

        try:
            with mock.patch.object(
                remote_script, "check_command_existence", return_value=True
            ):
                with mock.patch.object(remote_script, "shell_exec") as shell_exec:
                    cmd = remote_script.RunPy3Script(
                        "!py3", script_path, "arg with spaces", "semi;colon"
                    )
                    cmd.execute()
        finally:
            os.remove(script_path)

        command = shell_exec.call_args.args[0]
        self.assertIn(shell_quote("arg with spaces"), command)
        self.assertIn(shell_quote("semi;colon"), command)


class TestEnumerationCommandHardening(DummyContextTest):
    def _assert_strange_dirs_quotes_paths(self, module):
        path = "/target path;touch nope"
        with mock.patch.object(module, "check_command_existence", return_value=True):
            with mock.patch.object(
                module, "get_tmpfs_folder", return_value="/tmp/ffm tmp"
            ):
                with mock.patch.object(module, "shell_exec") as shell_exec:
                    cmd = module.StrangeDirs("!strange-dirs", path)
                    cmd.execute()

        commands = [call.args[0] for call in shell_exec.call_args_list]
        quoted_work_file = shell_quote(cmd.work_file)
        self.assertIn(quoted_work_file, commands[0])
        self.assertEqual(commands[1], "chmod +x %s" % quoted_work_file)
        self.assertEqual(
            commands[2],
            "python3 %s %s" % (quoted_work_file, shell_quote(path)),
        )
        self.assertEqual(commands[3], "rm %s" % quoted_work_file)

    def test_strange_dirs_quotes_paths_in_split_module(self):
        self._assert_strange_dirs_quotes_paths(enumeration_commands)

    def _assert_dirwalk_quotes_path(self, module):
        path = "/tmp/path with spaces;echo nope"
        with mock.patch.object(
            module.random, "choices", return_value=list("ABCDE")
        ):
            with mock.patch.object(module, "shell_exec", return_value="tree") as shell_exec:
                with mock.patch.object(module.os.path, "isdir", return_value=False):
                    with mock.patch.object(module.os, "mkdir") as mkdir:
                        with mock.patch("builtins.open", mock.mock_open()) as file_open:
                            cmd = module.DirWalk("!dirwalk", path)
                            cmd.execute()

        command = shell_exec.call_args.args[0]
        self.assertIn(shell_quote(path), command)
        expected_file = os.path.join("dirwalk", "ABCDE.txt")
        mkdir.assert_called_once_with("dirwalk")
        file_open.assert_called_once_with(expected_file, "w")

    def test_dirwalk_quotes_path_in_split_module(self):
        self._assert_dirwalk_quotes_path(enumeration_commands)

    def test_mtime_rejects_non_integer_input_in_split_module(self):
        with self.assertRaises(RuntimeError):
            enumeration_commands.Mtime("!mtime", "5;touch nope")


class TestStealthCommandHardening(DummyContextTest):
    def _assert_shred_quotes_path(self, module):
        path = "/tmp/file with spaces;echo nope"
        with mock.patch.object(module, "check_command_existence", return_value=True):
            with mock.patch.object(module, "shell_exec") as shell_exec:
                cmd = module.Shred("!shred", path)
                cmd.execute()

        self.assertEqual(
            shell_exec.call_args.args[0], "shred -uz %s" % shell_quote(path)
        )

    def test_shred_quotes_path_in_split_module(self):
        self._assert_shred_quotes_path(stealth_commands)


class TestNottySudoHardening(unittest.TestCase):
    def test_sudo_quotes_password_command_and_tempfile(self):
        old_context = notty_sudo.context
        notty_sudo.context = types.SimpleNamespace(
            active_session=types.SimpleNamespace(
                input_driver=types.SimpleNamespace(last_line="")
            )
        )

        try:
            with mock.patch.object(
                notty_sudo, "get_tmpfs_folder", return_value="/tmp/ffm tmp"
            ):
                with mock.patch.object(notty_sudo, "shell_exec") as shell_exec:
                    with mock.patch.object(notty_sudo, "pass_command") as pass_command:
                        cmd = notty_sudo.Sudo(
                            "!sudo",
                            "pa'ss word",
                            "sh",
                            "-c",
                            "echo hi;touch nope",
                        )
                        cmd.execute()
        finally:
            notty_sudo.context = old_context

        quoted_work_file = shell_quote(cmd.work_file)
        shell_commands = [call.args[0] for call in shell_exec.call_args_list]
        self.assertTrue(any(quoted_work_file in command for command in shell_commands))
        self.assertTrue(
            any(shell_quote("pa'ss word") in command for command in shell_commands)
        )
        self.assertIn(quoted_work_file, pass_command.call_args.args[0])
        self.assertIn(shell_quote("echo hi;touch nope"), pass_command.call_args.args[0])
