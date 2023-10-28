"""
    ffm.py by @JusticeRage and @ice-wzl

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
    def tag():
        return "Help"

    @staticmethod
    def usage():
        return "Usage: !dbg"

    def execute(self):
        write_str(
            "Current command prompt: %s\r\n"
            % context.active_session.input_driver.last_line.encode("UTF-8"),
            LogLevel.WARNING,
        )


register_plugin(Debug)
