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

import re
from commands.replacement_commands import SimpleAlias
from commands.run_py_script import RunPyScript

COMMAND_LIST = [SimpleAlias, RunPyScript]

def parse_commands(command_line):
    for c in COMMAND_LIST:
        if re.match(c.regexp(), command_line):
            # TODO: parse better?
            args = command_line.split(" ")
            command_instance = c(args)
            command_instance.execute()
            return True
    # No commands match, don't do anything.
    return False
