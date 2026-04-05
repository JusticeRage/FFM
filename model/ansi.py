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

# The SC/RC (save and restore cursor) work in an "absolute way", which means that
# they can only be used when the caller is certain that no scrolling is going to
# occur during the current operation.
SC = b"\x1b\x37"
RC = b"\x1b\x38"

END = b"\x1b\x4f\x46"
ICH = b"\x1b\x5b\x40"
CPL = b"\x1b\x5b\x46"

# The strings in this file are encoded in ASCII, as they're basically byte strings already.


def CUU(x=1):
    # Cursor up
    return ("\x1b\x5b%d\x41" % x).encode("ascii") if x > 1 else b"\x1b\x5b\x41"


def CUD(x=1):
    # Cursor up
    return ("\x1b\x5b%d\x42" % x).encode("ascii") if x > 1 else b"\x1b\x5b\x42"


def CUF(x=1):
    # Cursor forward
    return ("\x1b\x5b%d\x43" % x).encode("ascii") if x > 1 else b"\x1b\x5b\x43"


def CUB(x=1):
    # Cursor back
    return ("\x1b\x5b%d\x44" % x).encode("ascii") if x > 1 else b"\x1b\x5b\x44"


def CUP(x=0, y=0):
    # Cursor to position
    return ("\x1b\x5b%d;%d\x48" % (x, y)).encode("ascii")


def DCH(x=1):
    # Delete char
    return ("\x1b\x5b%d\x50" % x).encode("ascii")


def ED(how):
    """
    Erase data mnemonic.
    :param how: 0: Cursor to end of display, 1: Top of display through cursor, 2: Top to bottom of display
    """
    return ("\x1b\x5b%d\x4a" % how).encode("ascii")
