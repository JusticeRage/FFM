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

import types
from unittest import mock

import commands.notty_sudo as notty_sudo
from test.fixture.dummy_context import DummyContextTest


class TestNottySudoCommand(DummyContextTest):
    def test_command_assembly_quotes_password_tempfile_and_arguments(self):
        old_context = notty_sudo.context
        notty_sudo.context = types.SimpleNamespace(
            active_session=types.SimpleNamespace(
                input_driver=types.SimpleNamespace(last_line="")
            )
        )

        try:
            with mock.patch.object(
                notty_sudo.random, "choice", side_effect=list("ABCDEFGHIJKLMNOP")
            ), mock.patch.object(
                notty_sudo, "get_tmpfs_folder", return_value="/tmp/ffm tmp"
            ), mock.patch.object(
                notty_sudo, "shell_exec"
            ) as shell_exec, mock.patch.object(
                notty_sudo, "pass_command"
            ) as pass_command:
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

        expected_work_file = "'/tmp/ffm tmp/ABCDEFGHIJKLMNOP'"
        expected_password = "'pa'\"'\"'ss word'"
        expected_command = "sh -c 'echo hi;touch nope'"

        self.assertEqual(
            shell_exec.call_args_list[0].args[0],
            "cat <<'__EOF__' > {work_file}\n#!/bin/bash\nprintf '%s\\n' {password}\n__EOF__\n".format(
                work_file=expected_work_file,
                password=expected_password,
            ),
        )
        self.assertEqual(
            shell_exec.call_args_list[1].args[0],
            "chmod +x %s" % expected_work_file,
        )
        self.assertEqual(
            pass_command.call_args.args[0],
            "SUDO_ASKPASS={work_file} sudo -A {command} ; rm {work_file}".format(
                work_file=expected_work_file,
                command=expected_command,
            ),
        )
