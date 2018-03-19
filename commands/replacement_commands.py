"""
    ffm.py by @JusticeRage

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

import time
from commands.command_manager import register_plugin
from model.command.command import Command
from model.driver.input_api import *

class GetOS(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!os"

    @staticmethod
    def name():
        return "!os"

    @staticmethod
    def description():
        return "Prints the distribution of the current machine."

    def execute(self):
        shell_exec("cat /etc/*release*", print_output=True)

# -----------------------------------------------------------------------------

class PtySpawn(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!pty\s+"

    @staticmethod
    def name():
        return "!pty"

    @staticmethod
    def description():
        return "Spawns a PTY in the current shell."

    def execute(self):
        if context.active_session.input_driver.last_line is not None:
            raise RuntimeError("A TTY already seems to be present.")

        pass_command("python -c 'import pty; pty.spawn(\"/bin/sh\")'")
        # Sleep a little bit to allow the pty to be created.
        time.sleep(0.5)
        pass_command("unset HISTFILE")
        time.sleep(0.2)
        pass_command("stty -echo")



register_plugin(GetOS)
register_plugin(PtySpawn)
