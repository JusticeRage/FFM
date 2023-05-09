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
from model.plugin.command import Command
from model.driver.input_api import *

# -----------------------------------------------------------------------------

class GetOS(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!os($| )"

    @staticmethod
    def name():
        return "!os"

    @staticmethod
    def description():
        return "Prints the distribution of the current machine."

    @staticmethod
    def usage():
        return "Usage: !os"

    def execute(self):
        shell_exec("cat /etc/*release*", print_output=True)

# -----------------------------------------------------------------------------

class PtySpawn(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!pty($| )"

    @staticmethod
    def name():
        return "!pty"

    @staticmethod
    def description():
        return "Spawns a PTY in the current shell."

    @staticmethod
    def usage():
        return "Usage: !pty"

    def execute(self):
        if context.active_session.input_driver.last_line:
            raise RuntimeError("A TTY already seems to be present.")

        pass_command("script /dev/null")
        # Sleep a little bit to allow the pty to be created.
        time.sleep(0.2)
        pass_command("unset HISTFILE")
        pass_command("stty -echo")

# -----------------------------------------------------------------------------

class Debug(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!dbg($| )"

    @staticmethod
    def name():
        return "!dbg"

    @staticmethod
    def description():
        return "Prints debug information."

    @staticmethod
    def usage():
        return "Usage: !dbg"

    def execute(self):
        write_str("Current command prompt: %s\r\n" %
                  context.active_session.input_driver.last_line.encode("UTF-8"), LogLevel.WARNING)

class Suid(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!suid($| )"

    @staticmethod
    def name():
        return "!suid"

    @staticmethod
    def description():
        return "Finds SUID, SGID binaries on the current machine."

    @staticmethod
    def usage():
        return "Usage: !suid"

    def execute(self):
        write_str("SUID + SGID Binaries: \r\n", LogLevel.WARNING)
        shell_exec("find / -perm -4000 -type f ! -path '/dev/*' -exec ls -la {} \; 2>/dev/null; find / -perm -4000 -type f ! -path '/dev/*' -exec ls -la {} \; 2>/dev/null", print_output=True)


register_plugin(GetOS)
register_plugin(PtySpawn)
register_plugin(Debug)
register_plugin(Suid)
