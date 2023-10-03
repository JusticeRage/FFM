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

from model import context


def log(s):
    """
    Adds a string to the log file.
    This function checks whether a log file is currently specified and
    performs any processing on the input.
    :param s: The string to log.
    """
    if not context.log or not s:
        return

    s = re.sub(b"\x1b]0;.*?\x07", b"", s)  # Strip window title updates in all cases.
    if context.config["General"]["strip_color"]:
        s = re.sub(b"\x1b\[[0-?]*[ -/]*[@-~]", b"", s)  # Strip ANSI color codes

    context.log.write(s)
