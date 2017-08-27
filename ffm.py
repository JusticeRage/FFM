#!/usr/bin/env python3

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

import array
import argparse
import fcntl
import os
import select
import signal
import sys
import termios
import tty

import model.context as context
from model.driver import DefaultTerminalDriver
from model.session import Session

# -----------------------------------------------------------------------------

def update_window_size(signum=None, frame=None):
    """
    Handler for the WINCH signal. Forwards the new size to all the existing sessions.
    :return:
    """
    redraw = context.window_size is not None
    if redraw:
        context.terminal_driver.clear_line()
    winsz = array.array('h', [0, 0, 0, 0])
    fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, winsz, True)
    for s in context.sessions:
        fcntl.ioctl(s.master, termios.TIOCSWINSZ, winsz)
    context.window_size = [winsz[0], winsz[1]]
    if redraw:
        context.terminal_driver.draw_current_line()

# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Stealthy log file cleaner.")
    parser.add_argument("--debug", action="store_true", help="The username to remove from the connexion logs.")
    args = parser.parse_args()
    context.debug = args.debug

    context.terminal_driver = DefaultTerminalDriver()
    stdin_fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)
    old_handler = signal.signal(signal.SIGWINCH, update_window_size)
    tty.setraw(sys.stdin)

    context.active_session = Session()
    context.sessions.append(context.active_session)

    update_window_size()  # Set the correct window size in the PTY.

    try:
        while context.active_session and context.active_session.bash.poll() is None:
            try:
                r, w, e = select.select([sys.stdin, context.active_session.master], [], [])
                if sys.stdin in r:
                    typed_char = os.read(sys.stdin.fileno(), 1)
                    context.terminal_driver.handle_input(typed_char)
                elif context.active_session.master in r:
                    read = os.read(context.active_session.master, 2048)
                    if context.debug:
                        for c in read:
                            os.write(sys.stdout.fileno(), ("%02X " % ord(c)).encode("UTF-8"))
                    # Store the last line for possible future use
                    context.terminal_driver.last_line = read.split(b"\x07")[-1]  # TODO: NOT PORTABLE?
                    os.write(sys.stdin.fileno(), read)
            except select.error as e:
                if e[0] == 4:  # Interrupted system call. May be raised if SIGWINCH is received.
                    continue
                else:
                    raise
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
        signal.signal(signal.SIGWINCH, old_handler)


if __name__ == "__main__":
    main()
