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
import configparser
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
from processors.processor_manager import apply_processors, OUTPUT_PROCESSOR_LIST

# (\[?[\w-]+@[\w-]+[: ][/~].*)? [$#>] $ --> Prompts such as [user@machine ~]$
#                                           or user@machine:~/folder$
# ^[A-Za-z0-9 .-]+[>$#] $               --> Prompts like sh-4.2$
PROMPT_REGEXP = r"^(\[?[\w-]+@[\w-]+[: ][/~].*)?[$#>] $|^[A-Za-z0-9 .-]+[>$#] $"

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
    parser.add_argument("--config", "-c", help="The harness' configuration file.",
                        default=os.path.join(os.path.dirname(__file__), "ffm.conf"))
    parser.add_argument("--stdout", help="Redirect stdout to the target file.")
    args = parser.parse_args()
    context.debug_input = args.debug_input
    context.debug_output = args.debug_output
    context.stdout = open(args.stdout, "wb") if args.stdout is not None else sys.stdout

    # Print the banner
    print(random.choice(BANNERS) + "\n")
    print("FFM enabled. Type !list to see available commands and exit to quit.")

    # Check that the configuration file exists and is sane.
    if not os.path.exists(args.config):
        print("Could not find %s. Please provide it with the --config option." % args.config)
        return
    context.config = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes=("#", ";"))
    context.config.read(args.config)

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
                    try:
                        context.active_session.input_driver.handle_input(typed_char)
                    except RuntimeError as e:
                        os.write(context.stdout.fileno(), b"\r\n%s\r\n" % str(e).encode("UTF-8"))
                elif context.active_session.master in r:
                    read = os.read(context.active_session.master, 2048)
                    if context.debug_output:
                        for c in read:
                            os.write(context.stdout.fileno(), ("%02X " % c).encode("UTF-8"))

                    # Store the last line for future use
                    # Only work on the last line
                    last = read.split(b"\n")[-1]
                    if len(last) < 150 and b"\x07" in last:  # TODO: bug when cat-ing a binary file!
                        # This is motivated by my Debian shell's prompt containing weird \x07 bytes separating
                        # two prompt occurrences.
                        context.active_session.input_driver.last_line = last.split(b"\x07")[-1].decode("UTF-8", errors='ignore')
                    elif re.match(PROMPT_REGEXP, last.decode("UTF-8", errors='ignore'), re.UNICODE):
                        context.active_session.input_driver.last_line = last.decode("UTF-8")
                    else:
                        context.active_session.input_driver.last_line = ''

                    # Pass the output to the output driver for display after applying output processors.
                    (proceed, output) = apply_processors(read, OUTPUT_PROCESSOR_LIST)
                    if proceed:
                        context.active_session.output_driver.handle_bytes(output)
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
