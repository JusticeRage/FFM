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

from commands.command_manager import register_plugin
from model.driver.input_api import *

class SimpleAlias:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^wopwop"

    def execute(self):
        shell_exec("ls -l", print_output=True)
        output = shell_exec("id", print_output=True)
        if "ivan" in output:
            write_str("YAY!\r\n")
        elif "uid=0(root)" in output:
            write_str("I'm root! \o/")


register_plugin(SimpleAlias)
