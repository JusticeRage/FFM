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
import termios

import model.context as context
from model.driver.base import BaseDriver
from model.driver.passthrough import PassthroughDriver


class DefaultOutputDriver(BaseDriver):
    def __init__(self):
        self._saved_driver = None
        self._state = None
        self._parameters = ""

    def handle_input(self, typed_char):
        if self._state:
            self._state(typed_char)
        elif typed_char == 0x1B:
            self._state = self._state_escape
        else:
            os.write(context.stdout.fileno(), bytes([typed_char]))

    # -----------------------------------------------------------------------------
    # Parsing state machine below.
    # -----------------------------------------------------------------------------

    def _state_escape(self, c):
        if c == 0x5B:
            self._parameters = ""
            self._state = self._state_csi_entry
        else:
            os.write(context.stdout.fileno(), bytes([0x1B, c]))
            self._state = None

    # -----------------------------------------------------------------------------

    def _state_csi_entry(self, c):
        if c == 0x3F:  # Normally, "collect" action but we don't need this much.
            self._state = self._state_csi_param
        else:
            os.write(context.stdout.fileno(), bytes([0x1B, 0x5B, c]))
            self._state = None

    # -----------------------------------------------------------------------------

    def _state_csi_param(self, c):
        if 0x30 <= c <= 0x39 or c == 0x3B:
            self._parameters += chr(c)
        elif c == 0x68 and (self._parameters == "1049"):
            # DECSET. A program is trying to switch to the alternate screen.
            # Switch the driver to passthrough mode.
            self._saved_driver = context.active_session.input_driver
            context.active_session.input_driver = PassthroughDriver()
            #context.active_session.input_driver.handle_bytes(("\x1B\x5B\x3F%s\x68" % self._parameters).encode('ascii'))
            self._state = None
        elif c == 0x6C and (self._parameters == "1049"):
            # Exit alternate screen, restore the driver.
            #context.active_session.input_driver.handle_bytes(("\x1B\x5B\x3F%s\x6C" % self._parameters).encode('ascii'))
            context.active_session.input_driver = self._saved_driver
            self._saved_driver = None
            self._state = None
        else:
            os.write(context.stdout.fileno(), ("\x1B\x5B\x3F" + self._parameters + chr(c)).encode("ascii"))
            self._state = None
