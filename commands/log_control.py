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
from model.driver.input_api import *
from model.plugin.command import Command
from commands.command_manager import register_plugin
import os


class LogCommand(Command):
    def __init__(self, *args):
        self.target_file = None
        if len(args) >= 2:
            try:
                self.target_file = os.path.expanduser(args[1])
                if self.target_file.lower() == "off":  # !log off: disable logging.
                    return
                self.fd = open(self.target_file, "a+b")
            except OSError as e:
                raise RuntimeError(
                    "Could not open %s (%s)." % (self.target_file, str(e))
                )

    @staticmethod
    def disable_logging():
        """
        Function which disables any logging currently in place.
        :return: True if it succeeded, False otherwise.
        """
        if not context.log:
            return True
        try:
            context.log.close()
            context.log = None
            return True
        except OSError as e:
            write_str("Could not disable logging! (%s)\r\n" % str(e), LogLevel.ERROR)
            return False

    def execute(self):
        # No argument: display the current logging situation.
        if not self.target_file:
            if not context.log:
                write_str(
                    "This session is not currently logged. Call %s [filename] to enable it.\r\n"
                    % self.name()
                )
            else:
                write_str(
                    "This session is currently being logged to %s.\r\n"
                    % context.log.name
                )
            return

        # Disabling the logging
        if self.target_file == "off":
            if context.log is None:
                write_str("This session is not currently logged.\r\n")
            elif self.disable_logging():
                write_str("Logging has been disabled.\r\n")
            return

        # Enabling the logging
        if self.disable_logging() and self.fd:  # First, close the current log file.
            write_str("This session will now be logged to %s.\r\n" % self.target_file)
            context.log = self.fd

    @staticmethod
    def regexp():
        return r"^\s*\!log($| )"

    @staticmethod
    def name():
        return "!log"

    @staticmethod
    def usage():
        return "Usage: !log [filename] or !log off.\r\n"

    @staticmethod
    def description():
        return "Toggles logging the harness' input and output to a file."

    @staticmethod
    def tag():
        return "Enumeration"


register_plugin(LogCommand)
