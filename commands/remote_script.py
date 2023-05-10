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
from abc import abstractmethod

from model.driver.input_api import *
from model.plugin.command import Command
from commands.command_manager import register_plugin


class RemoteScript(Command):
    def __init__(self, *args):
        if len(args) < 2:
            raise RuntimeError("Received %d argument(s), expected 2." % len(args))
        self.script = os.path.expanduser(args[1])
        if not os.path.exists(self.script):
            raise RuntimeError("%s not found!" % self.script)
        self.script_args = " ".join(args[2:]) if len(args) > 2 else ""
        self.output_cleaner = None

        if not check_command_existence(self._get_interpreter()):
            raise RuntimeError("%s is not present on the machine!" % self._get_interpreter())

    @abstractmethod
    def _get_interpreter(self):
        """
        This method returns the name of the interpreter that should be used to run the remote script.
        :return:
        """
        raise NotImplementedError("Method _get_interpreter is not implemented!")

    @abstractmethod
    def _get_command_line(self):
        """
        The command line which should be called to execute the script.
        :return:
        """
        raise NotImplementedError("Method _get_command_line is not implemented!")

    @abstractmethod
    def _get_output_cleaner(self):
        """
        An optional function to clean up the output.
        :return:
        """
        return None

    def execute(self):
        with open(self.script, 'r') as f:
            contents = f.read()
            shell_exec(self._get_command_line().format(interpreter=self._get_interpreter(),
                                                       args=self.script_args,
                                                       script=contents),
                       print_output=True,
                       output_cleaner=self._get_output_cleaner())

# -----------------------------------------------------------------------------

class RunPyScript(RemoteScript):
    @staticmethod
    def regexp():
        return r"^\s*\!py($| )"

    @staticmethod
    def usage():
        write_str("Usage: !py [script on the local machine] [script arguments]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!py"

    @staticmethod
    def description():
        return "Runs a python script from the local machine in memory."

    def _get_interpreter(self):
        return "python"
    
        
    def _get_command_line(self):
        return "{interpreter} - {args} <<'__EOF__'\r\n{script}\r\n__EOF__"

    def _get_output_cleaner(self):
        # The Python interpreter displays a prompt while reading scripts from stdin. Strip it.
        return lambda s: s.lstrip(" >")

# -----------------------------------------------------------------------------

class RunPy3Script(RemoteScript):
    @staticmethod
    def regexp():
        return r"^\s*\!py3($| )"

    @staticmethod
    def usage():
        write_str("Usage: !py3 [script on the local machine] [script arguments]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!py3"

    @staticmethod
    def description():
        return "Runs a python3 script from the local machine in memory."

    def _get_interpreter(self):
        return "python3"
    
        
    def _get_command_line(self):
        return "{interpreter} - {args} <<'__EOF__'\r\n{script}\r\n__EOF__"

    def _get_output_cleaner(self):
        # The Python interpreter displays a prompt while reading scripts from stdin. Strip it.
        return lambda s: s.lstrip(" >")

# -----------------------------------------------------------------------------
class RunShScript(RemoteScript):
    @staticmethod
    def regexp():
        return r"^\s*\!sh($| )"

    @staticmethod
    def usage():
        write_str("Usage: !sh [script on the local machine] [script arguments]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!sh"

    @staticmethod
    def description():
        return "Runs a shell script from the local machine in memory."

    def _get_interpreter(self):
        return "sh"

    def _get_command_line(self):
        return "{interpreter} -s {args} <<'__EOF__'\r\n{script}\r\n__EOF__"

# -----------------------------------------------------------------------------

register_plugin(RunPyScript)
register_plugin(RunPy3Script)
register_plugin(RunShScript)
