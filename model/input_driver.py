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

import os
import re

import model.ansi as ansi
from model.base_driver import BaseDriver
from commands.replacement_commands import alias_test
from misc.stringutils import *
import model.context as context

# -----------------------------------------------------------------------------

def write(b):
    """
    Shorthand function that prints data to stdout. Mainly here to make the code
    more readable, and provide a single place to redirect writes if needed.

    :param b: The byte to print.
    :return:
    """
    os.write(context.stdout.fileno(), b)

# -----------------------------------------------------------------------------

def write_str(s):
    write(s.encode('UTF-8'))

# -----------------------------------------------------------------------------

class DefaultInputDriver(BaseDriver):
    """
    A partial implementation of a terminal emulator.
    It is based on the state machine located at http://vt100.net/emu/vt500_parser.png.
    Commands will be added on a need basis.
    """
    def __init__(self):
        self.input_buffer = ""
        self.cursor_position = 0
        self.state = self._state_ground  # Start of the state machine.
        self.parameters = ""
        self.unicode_buffer = bytearray()
        # A copy of the last line received from the PTY.
        # This is used to redraw the current line and compute the cursor's position.
        self.last_line = ""

    # -----------------------------------------------------------------------------

    def handle_input(self, typed_char):
        c = ord(typed_char)
        if context.debug_input:
            write_str("%02X " % c)

        # This non-canonical node takes priority if it's active, as
        # any subsequent byte is part of the character being read.
        if self.state == self._state_unicode_char:
            self.state(c)
            return

        # Anywhere node in the state machine.
        if c == 0x18 or c == 0x1A or 0x80 <= c <= 0x8F or 0x91 <= c <= 0x97 or c == 0x99 or c == 0x9A:
            # Execute
            raise RuntimeError("Not implemented (to handle here)! (Anywhere, 0x%02X)" % c)
            # self.state = self._state_ground
        elif c == 0x90:
            raise RuntimeError("Not implemented! (Anywhere, 0x%02X)" % c)
        elif c == 0x9B:
            self.state = self._state_csi_entry
            self._state_entry_clear()
        elif c == 0x9D:
            raise RuntimeError("Not implemented! (Anywhere, 0x%02X)" % c)
        elif c == 0x98 or c == 0x9E or c == 0x9F:
            raise RuntimeError("Not implemented! (Anywhere, 0x%02X)" % c)
        elif c == 0x9C:
            self.state = self._state_ground  # Ignore
        elif c == 0x1B:
            self.state = self._state_escape
            self._state_entry_clear()
        elif c == 0x02:
            # TODO: TEST COMMAND, DELETE
            write(b"\t\t")
            pass
        else:
            self.state(c)

    # -----------------------------------------------------------------------------

    def pop(self, amount=1):
        """
        Removes the last characters of the input buffer (based on the cursor).
        :param amount: The number of characters to remove.
        """
        if amount == 0:
            return
        if amount > len(self.input_buffer) - self.cursor_position:
            self.input_buffer = self.input_buffer[-self.cursor_position:]
        elif self.cursor_position == 0:
            self.input_buffer = self.input_buffer[:-amount]
        else:
            self.input_buffer = self.input_buffer[:-self.cursor_position-amount] + self.input_buffer[-self.cursor_position:]

    # -----------------------------------------------------------------------------

    def append(self, c):
        """
        Append a character to the input buffer at the position designated by the cursor.
        :param c: The character to append.
        """
        if self.cursor_position == 0 or c == '\r':
            self.input_buffer += c
        else:
            self.input_buffer = self.input_buffer[:-self.cursor_position] + c + \
                                self.input_buffer[-self.cursor_position:]

    # -----------------------------------------------------------------------------

    def clear_line(self):
        """
        Entirely deletes the current line. This is useful if it needs to be redrawn,
        for instance if the window has been resized.
        """
        # Calculate where the beginning of the line is (in terms of line wrapping).
        lines = (len(self.last_line) + len(self.input_buffer) - self.cursor_position) // context.window_size[1]
        if lines > 0:
            write(ansi.CUU(lines))  # Go to the line where the buffer starts.
        write(ansi.CUB(context.window_size[1]) + ansi.ED(0))  # Delete all after the caret.

    # -----------------------------------------------------------------------------

    def draw_current_line(self):
        """
        Prints the current line and positions the cursor accordingly.
        It is expected that the line has been erased before calling this function,
        for instance through clear_line()
        """
        write_str(self.last_line + self.input_buffer)
        x, y = self._backwards_move(self.cursor_position)
        self.relative_caret_move(x, y)

    # -----------------------------------------------------------------------------

    def backspace(self):
        """
        Handles the backspace (^H) character.
        """
        # Do nothing if there is nothing before the cursor.
        if len(self.input_buffer) - self.cursor_position == 0:
            return
        self.cursor_back(False)

        if self.cursor_position == 0:
            write(ansi.DCH())
            self.pop(1)
        else:
            write(ansi.SC)  # Save the cursor position.
            # Will the deletion cause the last line to be empty?
            if (len(self.last_line) - 1 + len(self.input_buffer)) % context.window_size[1] == 0:
                write_str(self.input_buffer[-self.cursor_position:] + "\r\n")
                write(ansi.DCH())
            else:
                write_str(self.input_buffer[-self.cursor_position:])
                write(ansi.DCH())
            self.pop(1)
            write(ansi.RC)  # Restore the cursor position.

    # -----------------------------------------------------------------------------

    def print_character(self, c):
        if self.cursor_position == 0:
            write_str(c)
            return

        # Will the addition cause au new line to be created?
        write_str(c + self.input_buffer[-self.cursor_position:])
        if (len(self.last_line) + len(self.input_buffer)) % context.window_size[1] == 0:
            write(b"\r\n")
        x, y = self._backwards_move(self.cursor_position, len(self.input_buffer))
        self.relative_caret_move(x, y)

    # -----------------------------------------------------------------------------

    def cursor_forward(self, adjust_internal_cursor=True):
        """
        Moves the on-screen caret back one position, going up to the previous line if needed.
        :param adjust_internal_cursor: Whether the internal cursor should be updated accordingly.
        This should always be True unless you have a very good reason not to do so.
        :return:
        """
        if self.cursor_position > 0:
            if not self.caret_at_eol():
                write(ansi.CUF())
            else:
                write(ansi.CUD() + ansi.CUB(context.window_size[1]))
            if adjust_internal_cursor:
                self.cursor_position -= 1

    # -----------------------------------------------------------------------------

    def cursor_back(self, adjust_internal_cursor=True):
        if self.cursor_position + 1 <= len(self.input_buffer):
            if not self.caret_at_sol():
                write(ansi.CUB())
            else:
                write(ansi.CUU() + ansi.CUF(context.window_size[1]))
            if adjust_internal_cursor:
                self.cursor_position += 1

    # -----------------------------------------------------------------------------

    def go_to_sol(self):
        """
        This function places the cursor and the caret on screen at the beginning of
        the input buffer. This is the behavior traditionally associated with ^A in
        terminals.
        This function also increments the internal cursor to len(self.input_buffer).
        """
        if self.cursor_position == len(self.input_buffer):
            return
        x, y = self._backwards_move(len(self.input_buffer) - self.cursor_position)
        self.relative_caret_move(x, y)
        self.cursor_position = len(self.input_buffer)

    # -----------------------------------------------------------------------------

    def go_to_eol(self):
        """
        Moves the caret to the end of the buffer on the screen. It works by simply
        redrawing the line, as the caret will be put at the end automatically.
        This function also puts the internal cursor to 0.
        """
        if self.cursor_position == 0:
            return
        x, y = self._forward_move(self.cursor_position)
        self.relative_caret_move(x, y)
        self.cursor_position = 0

    # -----------------------------------------------------------------------------

    @staticmethod
    def relative_caret_move(x, y):
        """
        Move the caret relatively to its current position.
        :param x: The number of lines to move. Negative numbers go upwards.
        :param y: The number of columns to move. Negative numbers go backwards.
        """
        command = b""
        if x > 0:
            command += ansi.CUU(x)
        if x < 0:
            command += ansi.CUD(-x)
        if y > 0:
            command += ansi.CUF(y)
        if y < 0:
            command += ansi.CUB(-y)
        if command:
            write(command)

    # -----------------------------------------------------------------------------

    def caret_at_eol(self):
        return (len(self.last_line) + len(self.input_buffer) - self.cursor_position) % context.window_size[1] \
               == context.window_size[1] - 1

    # -----------------------------------------------------------------------------

    def caret_at_sol(self):
        return (len(self.last_line) + len(self.input_buffer) - self.cursor_position) % context.window_size[1] == 0

    # -----------------------------------------------------------------------------

    def _backwards_move(self, move_length, start_offset=None):
        """
        This function computes the number of lines and columns that separate two positions
        in the input buffer on the screen.
        :param: move_length By how many characters we want to go back.
        :param: start_offset The index from which to start. Default is the cursor's position in the
        buffer.
        :return: (lines, columns), the number of lines and columns from the current
        position to move to the right place.
        """
        if start_offset is None:
            start_offset = len(self.input_buffer) - self.cursor_position

        if move_length > start_offset:
            move_length = start_offset

        # Case 1: the start and the target are on the same line.
        if ((start_offset + len(self.last_line)) // context.window_size[1] ==
            (start_offset + len(self.last_line) - move_length) // context.window_size[1]):
            return 0, -move_length
        # Case 2: the start and the target are on different lines.
        else:
            delta_lines = (len(self.last_line) + start_offset) // context.window_size[1] - \
                          (len(self.last_line) + start_offset - move_length) // context.window_size[1]
            delta_columns = (len(self.last_line) + start_offset - move_length) % context.window_size[1] - \
                            (len(self.last_line) + start_offset) % context.window_size[1]
            return delta_lines, delta_columns

    # -----------------------------------------------------------------------------

    def _forward_move(self, move_length, start_offset=None):
        """
        This function computes the number of lines and columns that separate two positions
        in the input buffer on the screen.
        :param: move_length By how many characters we want to go forward.
        :param: start_offset The index from which to start. Default is the cursor's position in the
        buffer.
        :return: (lines, columns), the number of lines and columns from the current
        position to move to the right place.
        """
        if start_offset is None:
            start_offset = len(self.input_buffer) - self.cursor_position

        if move_length > len(self.input_buffer) - start_offset:
            move_length = len(self.input_buffer) - start_offset

        # Case 1: the start and the target are on the same line.
        if ((start_offset + len(self.last_line)) // context.window_size[1] ==
                    (start_offset + len(self.last_line) + move_length) // context.window_size[1]):
            return 0, move_length
        # Case 2: the start and the target are on different lines.
        else:
            delta_lines = (len(self.last_line) + start_offset) // context.window_size[1] - \
                          (len(self.last_line) + start_offset + move_length) // context.window_size[1]
            delta_columns = (len(self.last_line) + start_offset + move_length) % context.window_size[1] - \
                            (len(self.last_line) + start_offset) % context.window_size[1]
            return delta_lines, delta_columns

    # -----------------------------------------------------------------------------

    def _backwards_word_move(self, word_characters=alphanum):
        """
        Moves the cursor backwards until the beginning of the current word (or the
        next one, if we're not currently in a word).
        :param word_characters: A list of characters that can be contained in a word.
        """
        # Skip any contiguous non-alphanum that may exist before the cursor.
        while self.cursor_position + 1 <= len(self.input_buffer) and \
                self.input_buffer[-self.cursor_position-1] not in word_characters:
            self.cursor_back()

        if self.cursor_position == len(self.input_buffer):
            return

        s = self.input_buffer[:-self.cursor_position] if self.cursor_position != 0 else self.input_buffer
        index = find_last_not_of(s, word_characters) + 1  # + 1 because we want to place the cursor after that char.
        if index == 0:  # No match found
            self.go_to_sol()
            self.cursor_position = len(self.input_buffer)
        else:
            offset = len(s) - index
            x, y = self._backwards_move(offset)
            self.relative_caret_move(x, y)
            self.cursor_position += offset

    # -----------------------------------------------------------------------------

    def _forward_word_move(self, word_characters=alphanum):
        """
        Moves the cursor forward until after the current word (or the
        next one, if we're not currently in a word).
        :param word_characters: A list of characters that can be contained in a word.
        """
        # Skip any contiguous non-alphanum that may exist at the cursor.
        while self.cursor_position != 0 and self.input_buffer[-self.cursor_position] not in word_characters:
            self.cursor_forward()

        if self.cursor_position == 0:  # Already at the end of the buffer.
            return

        s = self.input_buffer[-self.cursor_position:]
        index = find_first_not_of(s, word_characters)
        if index < 0:  # No match found
            self.go_to_eol()
            self.cursor_position = 0
        elif index == 0:  # Should be impossible.
            return
        else:
            x, y = self._forward_move(index)
            self.relative_caret_move(x, y)
            self.cursor_position -= index

    # -----------------------------------------------------------------------------
    # VT500 state machine below.
    # -----------------------------------------------------------------------------

    def _state_entry_clear(self):
        self.parameters = ""

    # -----------------------------------------------------------------------------

    def _state_ground(self, c):
        # Printable character: add it to the buffer and display it.
        if 0x20 <= c < 0x7F:
            self.append(chr(c))
            self.print_character(chr(c))
        elif c == 0x01:
            if self.cursor_position != len(self.input_buffer):
                self.go_to_sol()
        # ^E: go to the end of the line.
        elif c == 0x05:
            if self.cursor_position != 0:
                self.go_to_eol()
        # ^K: clear line starting from the cursor.
        elif c == 0x0B:
            if self.cursor_position > 0:
                write(ansi.ED(0))
                self.input_buffer = self.input_buffer[:-self.cursor_position]
                self.cursor_position = 0
        # ^L: clear screen
        elif c == 0x0C:
            write(ansi.CUP() + ansi.ED(2))  # Put the cursor at the top and delete all.
            self.draw_current_line()
        # Carriage return: validate and send to the PTY.
        elif c == 0x0D:
            # Place the cursor at EOL in order to avoid deleting part of the line with the output.
            if self.cursor_position != 0:
                self.go_to_eol()
            write(b"\r\n")
            # TODO: check for commands
            os.write(context.active_session.master, self.input_buffer.encode('UTF-8') + b'\r')
            self.input_buffer = ""
            self.cursor_position = 0
        # ^U: clear line up to the cursor.
        elif c == 0x15:
            if self.cursor_position == 0:
                self.clear_line()
                self.input_buffer = ""
                write_str(self.last_line)
            elif self.cursor_position != len(self.input_buffer):
                # Delete the whole line and rewrite the updated one, while keeping track
                # of where the cursor should be placed.
                self.clear_line()
                self.input_buffer = self.input_buffer[-self.cursor_position:]
                self.cursor_position = len(self.input_buffer)
                write_str(self.last_line)
                write(ansi.SC)
                write_str(self.input_buffer)
                write(ansi.RC)
        # Backspace (^H)
        elif c == 0x7F:
            self.backspace()
        elif 0 <= c <= 0x17 or c == 0x19 or 0x1C <= c <= 0x1F:
            # Execute
            raise RuntimeError("Not implemented (to handle here)! (Ground, 0x%02X)" % c)
        # Unicode character.
        elif 0xC2 <= c <= 0xF4:
            self.unicode_buffer = bytearray([c])
            self.state = self._state_unicode_char
        else:
            raise RuntimeError("Not implemented! (Ground, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _esc_dispatch(self, c):
        pass  # Not sure what I'm supposed to do here...

    # -----------------------------------------------------------------------------

    def _state_escape(self, c):
        if 0x00 <= c <= 0x17 or c == 0x19 or 0x1C <= c <= 0x1F:
            raise RuntimeError("Not implemented (to handle here)! (Everywhere, 0x%02X)" % c)
        elif c == 0x7F:  # Ignore
            return
        elif c == 0x5B:
            self.state = self._state_csi_entry
            self._state_entry_clear()
        elif 0x30 <= c <= 0x4E or 0x51 <= c <= 0x57 or c == 0x5A or c == 0x5C or 0x60 <= c <= 0x7E:
            self._esc_dispatch(c)
            self.state = self._state_ground
        # Not in the reference state machine. It however appears that recent keyboards map
        # the END / HOME keys to 1B 4F XX.
        elif c == 0x4F:
            self.state = self._state_escape_intermediate
        else:
            raise RuntimeError("Not implemented! (Escape, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _state_escape_intermediate(self, c):
        if c == 0x46:  # ESC O F - END key
            self.go_to_eol()
            self.state = self._state_ground
        elif c == 0x48: # ESC O H - HOME key
            self.go_to_sol()
            self.state = self._state_ground
        else:
            raise RuntimeError("Not implemented! (Escape, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _csi_dispatch(self, c):
        if c == 0x43:
            self.cursor_forward()
        elif c == 0x44:
            self.cursor_back()
        else:
            raise RuntimeError("Not implemented! (csi_dispatch, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _state_csi_entry(self, c):
        if c == 0x7F:
            return
        elif 0x0 <= c <= 0x17 or c == 0x19 or 0x1C <= c <= 0x1F:
            raise RuntimeError("Not implemented (to handle here)! (CSI Entry, 0x%02X)" % c)
        elif 0x40 <= c <= 0x7E:
            self._csi_dispatch(c)
            self.state = self._state_ground
        elif 0x30 <= c <= 0x38 or c == 0x3B:
            self.parameters += chr(c)
            self.state = self._state_csi_param
        else:
            raise RuntimeError("Not implemented! (CSI Entry, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _state_csi_param(self, c):
        if 0x30 <= c <= 0x38 or c == 0x3B:
            self.parameters += chr(c)
        # ^Right
        elif c == 0x43:
            self._forward_word_move()
            self.state = self._state_ground
        # ^Left
        elif c == 0x44:
            self._backwards_word_move()
            self.state = self._state_ground
        else:
            write_str("Parameters: " + self.parameters)
            raise RuntimeError("Not implemented! (CSI Param, 0x%02X)" % c)

    # -----------------------------------------------------------------------------

    def _state_unicode_char(self, c):
        """
        This state handles Unicode characters. It is *not* represented in the state
        machine diagram on which this code is based, and should therefore not be
        considered authoritative parsing!
        :param c: The new byte received.
        """
        self.unicode_buffer.append(c)
        # This test checks whether the buffer contains a 2, 3 or 4-byte unicode character
        # ready to be printed. No need to check the length in case of 2, because we can only
        # enter this state from Ground which initializes the buffer with 1 byte.
        if (0xC2 <= self.unicode_buffer[0] <= 0xDF) or \
           (0xE0 <= self.unicode_buffer[0] <= 0xEF and len(self.unicode_buffer) == 3) or \
           (0xF0 <= self.unicode_buffer[0] <= 0xF4 and len(self.unicode_buffer) == 4):
            unicode_char = self.unicode_buffer.decode("UTF-8")
            self.append(unicode_char)
            self.print_character(unicode_char)
            self.state = self._state_ground

    # -----------------------------------------------------------------------------

    def _debug(self, msg):
        """
        Dumps the contents of the input buffer. Only useful for debug purposes.
        :param msg: A prefix to display before the dump.
        :return:
        """
        write_str("\r\n" + msg + " ")
        for c in self.input_buffer:
            write_str("%c (%02X) " % (c, ord(c)))
