#!/usr/bin/env python3

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

import argparse
import array
import fcntl
import os
import random
import re
import select
import signal
import sys
import termios
import tty

from misc.banners import BANNERS
import model.context as context
from model.driver.input import DefaultInputDriver
from model.session import Session

PROMPT_REGEXP = r"^\[?[\w-]+@[\w-]+[: ][/~].*[$#] $|^\$ $|^[A-Za-z ]+> $"

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
    parser = argparse.ArgumentParser(description="Freedom Fighting Mode.")
    parser.add_argument("--debug-input", action="store_true", help="Toggle debugging of the user input.")
    parser.add_argument("--debug-output", action="store_true", help="Toggle debugging of the terminal output.")
    parser.add_argument("--stdout", help="Redirect stdout to the target file.")
    args = parser.parse_args()
    context.debug_input = args.debug_input
    context.debug_output = args.debug_output
    context.stdout = open(args.stdout, "wb") if args.stdout is not None else sys.stdout

    # Print the banner
    print(random.choice(BANNERS) + "\n")

    context.terminal_driver = DefaultInputDriver()
    stdin_fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)
    old_handler = signal.signal(signal.SIGWINCH, update_window_size)
    tty.setraw(context.stdin)

    context.active_session = Session()
    context.sessions.append(context.active_session)

    update_window_size()  # Set the correct window size in the PTY.

    try:
        while context.active_session and context.active_session.bash.poll() is None:
            try:
                r, w, e = select.select([sys.stdin, context.active_session.master], [], [], 1)
                if sys.stdin in r:
                    typed_char = os.read(sys.stdin.fileno(), 1)
                    context.active_session.input_driver.handle_input(typed_char)
                elif context.active_session.master in r:
                    read = os.read(context.active_session.master, 2048)
                    if context.debug_output:
                        for c in read:
                            os.write(sys.stdout.fileno(), ("%02X " % c).encode("UTF-8"))
                    # Store the last line for future use # TODO: NOT PORTABLE!
                    # This is motivated by my Debian shell's prompt containing weird \x07 bytes separating
                    # two prompt occurrences.
                    if len(read) < 150 and b"\x07" in read:  # TODO: bug when cat-ing a binary file!
                        context.active_session.input_driver.last_line = read.split(b"\x07")[-1].decode("UTF-8", errors='ignore')
                    elif re.match(PROMPT_REGEXP, read.decode("UTF-8", errors='ignore'), re.UNICODE):
                        context.active_session.input_driver.last_line = read.decode("UTF-8")
                    else:
                        context.active_session.input_driver.last_line = ''
                    # Pass the output to the output driver for display.
                    context.active_session.output_driver.handle_bytes(read)
            except select.error as e:
                if "[Errno 4]" in str(e):  # Interrupted system call. May be raised if SIGWINCH is received.
                    continue
                else:
                    raise
            # Pretty printing for unimplemented opcodes: no need for a full trace. Probably remove that in the future.
            except RuntimeError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("\r\n%s (%s, line %d)\r" % (str(e), filename, exc_tb.tb_lineno))
                return

        # Bash has finished running
        print("FFM disabled.\r")

    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
        signal.signal(signal.SIGWINCH, old_handler)


if __name__ == "__main__":
    main()
