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
SC  = b"\x1B\x37"
RC  = b"\x1B\x38"

END = b"\x1B\x4F\x46"
ICH = b"\x1B\x5B\x40"
CPL = b"\x1B\x5B\x46"

# The strings in this file are encoded in ASCII, as they're basically byte strings already.

def CUU(x=1):
    # Cursor up
    return ("\x1B\x5B%d\x41" % x).encode('ascii') if x > 1 else b"\x1B\x5B\x41"

def CUD(x=1):
    # Cursor up
    return ("\x1B\x5B%d\x42" % x).encode('ascii') if x > 1 else b"\x1B\x5B\x42"

def CUF(x=1):
    # Cursor forward
    return ("\x1B\x5B%d\x43" % x).encode('ascii') if x > 1 else b"\x1B\x5B\x43"

def CUB(x=1):
    # Cursor back
    return ("\x1B\x5B%d\x44" % x).encode('ascii') if x > 1 else b"\x1B\x5B\x44"

def CUP(x=0, y=0):
    # Cursor to position
    return ("\x1B\x5B%d;%d\x48" % (x, y)).encode('ascii')

def DCH(x=1):
    # Delete char
    return ("\x1B\x5B%d\x50" % x).encode('ascii')

def ED(how):
    """
    Erase data mnemonic.
    :param how: 0: Cursor to end of display, 1: Top of display through cursor, 2: Top to bottom of display
    """
    return ("\x1B\x5B%d\x4A" % how).encode('ascii')
