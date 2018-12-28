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
from enum import Enum
import misc.logging
from model import context
import os
import random
import re
import select
import string
import sys

MARKER_STR = ''.join(random.choice(string.ascii_letters) for i in range(32))
MARKER = MARKER_STR.encode("UTF-8")

WARNING = '\033[93m'
ERROR = '\033[91m'
ENDC = '\033[0m'

# -----------------------------------------------------------------------------

def write(b):
    """
    Shorthand function that prints data to stdout. Mainly here to make the code
    more readable, and provide a single place to redirect writes if needed.
    :param b: The byte to print.
    """
    out_fd = context.stdout.fileno() if context.stdout else sys.stdout.fileno()
    os.write(out_fd, b)

# -----------------------------------------------------------------------------

class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

# -----------------------------------------------------------------------------

def write_str_internal(s):
    """
    Shorthand function which directly prints a string to stdout.
    In particular, this function bypasses any logging. Plugin developers should
    use write_str instead.
    :param s: The string to print.
    """
    write(s.encode('UTF-8'))

# -----------------------------------------------------------------------------

def write_str(s, level=LogLevel.INFO):
    """
    Function used to print strings to stdout.
    :param s: The string to print.
    :param level: The importance of the message. Either INFO, WARNING or ERROR.
    """
    if level == LogLevel.WARNING:
        msg = WARNING + s + ENDC
    elif level == LogLevel.ERROR:
        msg = ERROR + s + ENDC
    else:
        msg = s
    # Log the message if a log file is opened:
    misc.logging.log(msg.encode('UTF-8'))
    write_str_internal(msg)

# -----------------------------------------------------------------------------

def _read_all_output(timeout):
    """
    Reads all the output of a command from the current terminal.
    This works by reading from the TTY until a command prompt is found.
    /!\ The end marker is expected to be the same as the one before the
    command was executed! This means that if the command changes the prompt,
    (ie. cd, etc.) this function will never return!
    :param timeout The maximum amount of time to wait for the end of the
    output.
    :return:
    """
    output = b""
    end_marker = context.active_session.input_driver.last_line.encode("UTF-8")
    if not end_marker:
        # No prompt to detect. Add a marker manually to know when to stop reading the output.
        end_marker = MARKER
        os.write(context.active_session.master, ("echo -n %s\r" % MARKER_STR).encode("UTF-8"))
    # Strip ascii color codes and such when looking for the end marker.
    while not re.sub(b"\x1b]0;.*?\x07|\x1b\[[0-?]*[ -/]*[@-~]", b"", output).endswith(end_marker):
        r, _, _ = select.select([context.active_session.master], [], [], timeout)
        if context.active_session.master in r:
            output += os.read(context.active_session.master, 4096)
        else:
            write_str("Timeout reached; giving up on trying to capture the output.\r\n", LogLevel.ERROR)
            return output.decode("UTF-8")

    # The last line of the output should be a new prompt or the marker. Exclude it from
    # the output.
    index = output.rfind(b"\r\n")
    if index != -1:
        return output[:index].decode("UTF-8")
    else:  # No new line in the output: it's only the marker then.
        return ""

# -----------------------------------------------------------------------------

def pass_command(command):
    """
    Simply passes a command to the underlying shell. The output is completely
    ignored.
    :param command: The command to run.
    :return: None
    """
    os.write(context.active_session.master, ("%s\r" % command).encode("UTF-8"))

# -----------------------------------------------------------------------------

def shell_exec(command, print_output=False, output_cleaner=None, timeout=300):
    """
    Executes a command in the shell.
    /!\ Do not run commands that change the prompt (ie. cd, etc.)!
    :param command: The command to run.
    :param print_output: Whether the output of the command should be printed
    to stdout.
    :param output_cleaner: A function to call on the output to preprocess it
    before printing it (ex: remove trailing newlines, etc.)
    :param timeout: The maximum time to wait before giving up on trying to
    read the output of the command.
    :return: The output of the command.
    """
    pass_command(command)
    output = _read_all_output(timeout)
    if output_cleaner and callable(output_cleaner):
        output = output_cleaner(output)
    if print_output and output:
        write_str(output + "\r\n")
    return output

# -----------------------------------------------------------------------------

def file_exists(path):
    """
    Tests whether a file exists.
    :param path: The path to test.
    :return: True if the file exists, False otherwise.
    """
    output = shell_exec("test -f %s ; echo $?" % path, timeout=30)
    return int(output) == 0

# -----------------------------------------------------------------------------

def is_directory(path):
    """
    Tests whether a given file is a directory.
    :param path: The path to test
    :return: True if the file is a directory.
    """
    output = shell_exec("test -d %s ; echo $?" % path, timeout=30)
    return int(output) == 0

# -----------------------------------------------------------------------------

def check_command_existence(cmd):
    """
    Verifies that a given command exists on the machine.
    :param cmd: The command whose existence we want to check.
    :return: True if the command is present on the system, False otherwise.
    """
    output = shell_exec("command -v %s >/dev/null ; echo $?" % cmd, timeout=30)
    return int(output) == 0
