"""
FFM by @JusticeRage

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import tempfile
import types
from unittest import mock

import commands.remote_elf as remote_elf
import commands.remote_script as remote_script
from test.fixture.dummy_context import DummyContextTest


class _FakeProgressBar:
    def __init__(self, *args, **kwargs):
        self.updates = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, amount):
        self.updates.append(amount)


class TestRemoteScriptCommand(DummyContextTest):
    def _execute_script(self, command_cls, script_contents, *script_args):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write(script_contents)
            script_path = handle.name

        try:
            with mock.patch.object(
                remote_script, "check_command_existence", return_value=True
            ), mock.patch.object(remote_script, "shell_exec") as shell_exec:
                cmd = command_cls(
                    "!" + command_cls.name().lstrip("!"), script_path, *script_args
                )
                cmd.execute()
        finally:
            os.remove(script_path)

        return shell_exec, cmd

    def test_heredoc_delimiter_moves_when_script_contains_default_delimiter(self):
        shell_exec, _ = self._execute_script(
            remote_script.RunPyScript,
            "print('__FFM_EOF__')\n",
        )

        command = shell_exec.call_args.args[0]
        self.assertEqual(
            command,
            "python -  <<'__FFM_EOF___X'\r\nprint('__FFM_EOF__')\n\r\n__FFM_EOF___X",
        )

    def test_python_and_shell_commands_quote_arguments(self):
        script_cases = [
            (
                remote_script.RunPyScript,
                "print('hello')\n",
                "python - 'arg with spaces' 'semi;colon' <<'__FFM_EOF__'\r\nprint('hello')\n\r\n__FFM_EOF__",
            ),
            (
                remote_script.RunPy3Script,
                "print('hello')\n",
                "python3 - 'arg with spaces' 'semi;colon' <<'__FFM_EOF__'\r\nprint('hello')\n\r\n__FFM_EOF__",
            ),
            (
                remote_script.RunShScript,
                "echo hello\n",
                "sh -s 'arg with spaces' 'semi;colon' <<'__FFM_EOF__'\r\necho hello\n\r\n__FFM_EOF__",
            ),
        ]
        args = ("arg with spaces", "semi;colon")

        for command_cls, script_contents, expected in script_cases:
            with self.subTest(command_cls=command_cls.__name__):
                shell_exec, _ = self._execute_script(
                    command_cls, script_contents, *args
                )
                command = shell_exec.call_args.args[0]
                self.assertEqual(command, expected)
                if command_cls is remote_script.RunShScript:
                    self.assertIsNone(shell_exec.call_args.kwargs["output_cleaner"])
                else:
                    self.assertTrue(
                        callable(shell_exec.call_args.kwargs["output_cleaner"])
                    )


class _RemoteElfCommandSetupTest(DummyContextTest):
    def _build_context(self):
        return types.SimpleNamespace(active_session=types.SimpleNamespace(master=123))

    def _run_command(
        self,
        interpreter_presence,
        interpreter_versions,
        *args,
        program_contents=b"fake-binary"
    ):
        with tempfile.NamedTemporaryFile("wb", delete=False) as handle:
            handle.write(program_contents)
            program_path = handle.name

        calls = []

        def fake_shell_exec(command, *shell_args, **shell_kwargs):
            calls.append((command, shell_args, shell_kwargs))
            for interpreter, major_version in interpreter_versions.items():
                if command == (
                    '%s -c "import sys; print(sys.version_info[0])"' % interpreter
                ):
                    return str(major_version)
            if "import ctypes" in command:
                return "0"
            return "ok"

        try:
            old_context = remote_elf.context
            remote_elf.context = self._build_context()
            with mock.patch.object(
                remote_elf,
                "check_command_existence",
                side_effect=lambda interpreter: interpreter_presence.get(
                    interpreter, False
                ),
            ), mock.patch.object(
                remote_elf, "shell_exec", side_effect=fake_shell_exec
            ), mock.patch.object(
                remote_elf.os, "write"
            ) as os_write, mock.patch.object(
                remote_elf.tqdm, "tqdm", return_value=_FakeProgressBar()
            ), mock.patch.object(
                remote_elf, "write_str"
            ):
                cmd = remote_elf.RemoteElf("!elf", program_path, *args)
                cmd.execute()
        finally:
            remote_elf.context = old_context
            os.remove(program_path)

        return cmd, calls, os_write, program_path


class TestRemoteElfCommandSetup(_RemoteElfCommandSetupTest):
    def test_smoke_setup_prefers_python3_and_preserves_arguments(self):
        cmd, calls, os_write, program_path = self._run_command(
            {"python3": True, "python": True, "python2.6": True},
            {"python3": 3, "python": 3, "python2.6": 2},
            "--flag",
            "path with spaces",
            "semi;colon",
        )

        expected_argv = [
            os.path.basename(program_path),
            "--flag",
            "path with spaces",
            "semi;colon",
        ]
        self.assertEqual(cmd.program_args, expected_argv)
        self.assertEqual(cmd.interpreter, "python3")
        self.assertEqual(
            os_write.call_args_list[0].args[1],
            b"python3 - <<'__EOF__'\r\np = ''\r\n",
        )
        stager = calls[-1][0]
        expected_staged_argv = (
            'os.execv("/proc/self/fd/%i" % fd, ' + repr(expected_argv) + ")"
        )
        self.assertIn(expected_staged_argv, stager)
        self.assertTrue(stager.endswith("\r\n__EOF__"))
        self.assertEqual(
            calls[0][0],
            'python3 -c "import sys; print(sys.version_info[0])"',
        )
        self.assertEqual(
            calls[1][0],
            "python3 -c \"import ctypes;print(ctypes.CDLL(None).syscall(319, '', 0))\"",
        )

    def test_smoke_setup_uses_generic_python_when_it_is_python2(self):
        cmd, calls, os_write, program_path = self._run_command(
            {"python3": False, "python": True, "python2.6": True},
            {"python": 2, "python2.6": 2},
            "--flag",
            "path with spaces",
            "semi;colon",
        )

        expected_argv = [
            os.path.basename(program_path),
            "--flag",
            "path with spaces",
            "semi;colon",
        ]
        self.assertEqual(cmd.program_args, expected_argv)
        self.assertEqual(cmd.interpreter, "python")
        self.assertEqual(
            os_write.call_args_list[0].args[1],
            b"python - <<'__EOF__'\r\np = ''\r\n",
        )
        stager = calls[-1][0]
        expected_staged_argv = (
            'os.execv("/proc/self/fd/%i" % fd, ' + repr(expected_argv) + ")"
        )
        self.assertIn(expected_staged_argv, stager)
        self.assertTrue(stager.endswith("\r\n__EOF__"))
        self.assertEqual(
            calls[0][0],
            'python -c "import sys; print(sys.version_info[0])"',
        )
        self.assertEqual(
            calls[1][0],
            "python -c 'import ctypes;print ctypes.CDLL(None).syscall(319, \"\", 0)'",
        )

    def test_smoke_setup_falls_back_to_any_python2_binary(self):
        cmd, calls, os_write, program_path = self._run_command(
            {"python3": False, "python": False, "python2.6": True},
            {"python2.6": 2},
            "--flag",
            "path with spaces",
            "semi;colon",
        )

        expected_argv = [
            os.path.basename(program_path),
            "--flag",
            "path with spaces",
            "semi;colon",
        ]
        self.assertEqual(cmd.program_args, expected_argv)
        self.assertEqual(cmd.interpreter, "python2.6")
        self.assertEqual(
            os_write.call_args_list[0].args[1],
            b"python2.6 - <<'__EOF__'\r\np = ''\r\n",
        )
        self.assertEqual(
            calls[0][0],
            'python2.6 -c "import sys; print(sys.version_info[0])"',
        )

    def test_constructor_rejects_when_no_supported_python_is_available(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as handle:
            handle.write(b"fake-binary")
            program_path = handle.name

        try:
            with mock.patch.object(
                remote_elf, "check_command_existence", return_value=False
            ):
                with self.assertRaises(RuntimeError):
                    remote_elf.RemoteElf("!elf", program_path)
        finally:
            os.remove(program_path)
