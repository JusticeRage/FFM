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
import os
import re
from model.plugin.command import Command
from model.driver.input_api import write_str, LogLevel

COMMAND_LIST = set()

def register_plugin(plugin):
    if not issubclass(plugin, Command):
        write_str("Tried to register %s which is not a valid command!\r\n" % str(plugin), LogLevel.ERROR)
        return
    elif plugin in COMMAND_LIST:
        write_str("Tried to register %s twice!\r\n" % str(plugin), LogLevel.ERROR)
        return
    else:
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
                    write_str("Command failed with error: %s\r\n" % str(e), LogLevel.WARNING)
            return True
    # No commands match, don't do anything.
    return False

# -----------------------------------------------------------------------------

class ListPlugins(Command):
    def __init__(self, *nargs, **kwargs):
        if len(nargs) == 1:
            self.tag = None 
        elif len(nargs) == 2:
            self.tag = nargs[1]
        else:
            raise RuntimeError("Received %d argument(s), expected 1 or 2." % len(nargs))

    def execute(self):
        #if !list is provided with no args then print *
        #if !list all is provided then do that as well 
        write_str("List of commands available:\r\n", LogLevel.WARNING)
        strings = []
        if self.tag == None or self.tag == "all": 
            for c in COMMAND_LIST:
                strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            # Sort the plugins by alphabetical order.
            for s in sorted(strings):
                write_str(s)
        elif self.tag == "execution":
            for c in COMMAND_LIST:
                if c.tag() == "Execution":
                    strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            for s in sorted(strings):
                write_str(s)
        elif self.tag == "tags":
            for c in COMMAND_LIST:
                strings.append("\t %s\r\n" % (c.tag()))
            for s in sorted(set(strings)):
                write_str(s.lower())
        elif self.tag == "transfer":
            for c in COMMAND_LIST:
                if c.tag() == "Transfer":
                    strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            for s in sorted(strings):
                write_str(s)
        elif self.tag == "stealth":
            for c in COMMAND_LIST:
                if c.tag() == "Stealth":
                    strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            for s in sorted(strings):
                write_str(s)
        elif self.tag == "enumeration":
            for c in COMMAND_LIST:
                if c.tag() == "Enumeration":
                    strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            for s in sorted(strings):
                write_str(s)
        elif self.tag == "help":
            for c in COMMAND_LIST:
                if c.tag() == "Help":
                    strings.append("\t%s --> %s\r\n" % (c.name(), c.description()))
            for s in sorted(strings):
                write_str(s)
        else:
            write_str(self.usage())

    @staticmethod
    def regexp():
        return r"^\s*\!list($| )"

    @staticmethod
    def name():
        return "!list"

    @staticmethod
    def description():
        return "Show the list of available commands/module tags."
    
    @staticmethod
    def tag():
        return "Help"

    @staticmethod
    def usage():
        write_str("Usage:\r\n\t!list --> see all commands\r\n\t!list all --> see all commands\r\n\t!list tags --> see different module tags\r\n\t!list <tag-name> --> see commands related to <tag-name>\r\n", LogLevel.INFO)

# -----------------------------------------------------------------------------
# This section registers all known commands at startup. It starts by adding
# "builtin" commands, and then scans the current folder for any .py file.
# -----------------------------------------------------------------------------

# Register all "builtin" commands
register_plugin(ListPlugins)
# Look for commands in the folder
folder = os.path.dirname(__file__)
for f in glob.glob(os.path.join(folder, "*.py")):
    if f == __file__ or f.endswith("__init__.py"):
        continue
    with open(f, "rb") as fd:
        exec(compile(fd.read(), f, 'exec'))

