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
import pty
import subprocess
import termios

from model.driver import input, output


class Session:
    def __init__(self):
        self.master, self.slave = pty.openpty()
        self.bash = subprocess.Popen([os.getenv("SHELL", "/bin/bash")],
                                     preexec_fn=os.setsid,
                                     stdin=self.slave,
                                     stdout=self.slave,
                                     stderr=self.slave,
                                     universal_newlines=True)
        self.disable_echo()
        self.input_driver = input.DefaultInputDriver()
        self.output_driver = output.DefaultOutputDriver()

    # -----------------------------------------------------------------------------

    def enable_echo(self):
        """
        Enables echoing typed characters in the session.
        :return:
        """
        flags = termios.tcgetattr(self.master)
        flags[3] |= termios.ECHO
        termios.tcsetattr(self.master, termios.TCSANOW, flags)

    # -----------------------------------------------------------------------------

    def disable_echo(self):
        """
        Disables echoing typed characters in the session.
        :return:
        """
        flags = termios.tcgetattr(self.master)
        flags[3] &= ~termios.ECHO
        termios.tcsetattr(self.master, termios.TCSANOW, flags)
