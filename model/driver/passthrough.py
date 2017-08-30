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

import model.context
from model.driver.base import BaseDriver


class PassThroughDriver(BaseDriver):
    """
    Terminal driver which does nothing but forward whatever it receives.
    """
    def __init__(self, fd=None):
        self.fd = fd if fd is not None else model.context.active_session.master

    def handle_input(self, typed_char):
        if type(typed_char) == bytes:
            os.write(self.fd, typed_char)
        elif type(typed_char) == int:
            os.write(self.fd, bytes([typed_char]))
