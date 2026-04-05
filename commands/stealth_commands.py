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
    def tag():
        return "Stealth"

    @staticmethod
    def usage():
        return "Usage: !pty"

    def execute(self):
        if context.active_session.input_driver.last_line:
            raise RuntimeError("A TTY already seems to be present.")

        pass_command("script /dev/null")
        # Sleep a little bit to allow the pty to be created.
        time.sleep(0.2)
        write_str("Set your rows and cols correctly:\r\n", LogLevel.WARNING)
        write_str("\tstty -a #in a local window of the same size\r\n")
        write_str("\tstty rows= cols= \r\n")
        pass_command("unset HISTFILE HISTFILESIZE HISTSIZE PROMPT_COMMAND")
        pass_command("stty -echo")
        pass_command("export TERM=xterm")
        pass_command("unset SSH_CONNECTION")


# -----------------------------------------------------------------------------

class Shred(Command):
    def __init__(self, *args, **kwargs):
        self.file = None
        if len(args) == 2:
            self.file = args[1]
        else:
            raise RuntimeError(
                "Received %d argument(s), expected 2. !shred <file>" % len(args)
            )

    @staticmethod
    def regexp():
        return r"^\s*\!shred($| )"

    @staticmethod
    def name():
        return "!shred"

    @staticmethod
    def description():
        return "Secure file deletion with shred or dd/rm"

    @staticmethod
    def tag():
        return "Stealth"

    @staticmethod
    def usage():
        return "Usage: !shred [file]"

    def execute(self):
        quoted_file = shell_quote(self.file)
        if not check_command_existence("shred"):
            shell_exec(
                'dd if=/dev/urandom of={file} bs=1k count="$(du -sk {file} | cut -f1)" conv=notrunc 2>/dev/null; rm -f {file}'.format(
                    file=quoted_file
                ),
                print_output=True,
            )
            write_str("{} deleted with dd/rm\r\n".format(self.file), LogLevel.ERROR)
        else:
            shell_exec("shred -uz {}".format(quoted_file))
            write_str("{} deleted with shred\r\n".format(self.file), LogLevel.ERROR)


register_plugin(PtySpawn)
register_plugin(Shred)
