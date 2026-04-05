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
import random
import string

from model.driver.input_api import *
from model.plugin.command import Command
from commands.command_manager import register_plugin


class Sudo(Command):
    """
    This command does some askpass sleight of hand to allow sudo invocations when no TTY
    is present.
    Inspired from https://github.com/zMarch/Orc/.
    """

    def __init__(self, *args):
        if context.active_session.input_driver.last_line:
            raise RuntimeError("A TTY already seems to be present.")
        if len(args) < 3:
            raise RuntimeError(
                "Received %d argument(s), expected at least 3." % len(args)
            )

        workdir = get_tmpfs_folder()
        if not workdir:
            raise RuntimeError("Could not find a suitable tmpfs folder to work in!")
        self.work_file = os.path.join(
            workdir, "".join(random.choice(string.ascii_letters) for _ in range(16))
        )
        self.password = args[1]
        self.command = args[2:]

    def execute(self):
        quoted_work_file = shell_quote(self.work_file)
        quoted_command = shell_join(self.command)
        # Create an askpass script
        shell_exec(
            "cat <<'__EOF__' > {work_file}\n#!/bin/bash\nprintf '%s\\n' {password}\n__EOF__\n".format(
                work_file=quoted_work_file, password=shell_quote(self.password)
            )
        )
        shell_exec("chmod +x %s" % quoted_work_file)
        # Call sudo with the askpass script.
        # pass_command is used because sudo has a very weird behavior:
        # > SUDO_ASKPASS=/tmp/test.sh sudo -A id ; echo -n "AAAAAA"
        # [...]
        # sudoAAAAAA: 3 incorrect password attempts
        # The echo data is mangled with sudo's output which screws with FFM's internals.
        pass_command(
            "SUDO_ASKPASS={work_file} sudo -A {command} ; rm {work_file}".format(
                work_file=quoted_work_file, command=quoted_command
            )
        )

    @staticmethod
    def regexp():
        return r"^\s*\!sudo($| )"

    @staticmethod
    def usage():
        write_str(
            "Usage: !sudo [password] [optional sudo arguments] command\r\n",
            LogLevel.WARNING,
        )

    @staticmethod
    def name():
        return "!sudo"

    @staticmethod
    def description():
        return "Invoke sudo without a TTY."

    @staticmethod
    def tag():
        return "Stealth"


register_plugin(Sudo)
