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

import glob
import importlib
import os
import re
from model.driver.input_api import write_str, LogLevel

COMMAND_LIST = set()

def register_plugin(plugin):
    COMMAND_LIST.add(plugin)

def parse_commands(command_line):
    for c in COMMAND_LIST:
        if re.match(c.regexp(), command_line):
            # TODO: parse better?
            args = command_line.split()
            try:
                command_instance = c(*args)
            except RuntimeError as e:  # The constructor throws: show the command usage.
                c.usage()
                if str(e):
                    write_str("%s\r\n" % str(e), LogLevel.WARNING)
            else:
                try:
                    command_instance.execute()
                except Exception as e:
                    write_str("Command failed with error: %s.\r\n" % str(e))
            return True
    # No commands match, don't do anything.
    return False

# -----------------------------------------------------------------------------

class ListPlugins:
    def __init__(self, *nargs, **kwargs):
        pass

    def execute(self):
        write_str("TEST")

    @staticmethod
    def regexp():
        return r"^\!list"

    @staticmethod
    def name():
        return "!list"

    @staticmethod
    def usage():
        write_str("Usage: !list\r\n")

# -----------------------------------------------------------------------------
# This section registers all known commands at startup. It starts by adding
# "builtin" commands, and then scans the current folder for any .py file.
# -----------------------------------------------------------------------------

# Register all known commands
register_plugin(ListPlugins)
# Look for commands in the folder
folder = os.path.dirname(__file__)
for f in glob.glob(os.path.join(folder, "*.py")):
    if f == __file__ or f.endswith("__init__.py"):
        continue
    with open(f, "rb") as fd:
        exec(compile(fd.read(), f, 'exec'))
