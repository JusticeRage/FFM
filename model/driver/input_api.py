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
from model import context

# -----------------------------------------------------------------------------

def write(b):
    """
    Shorthand function that prints data to stdout. Mainly here to make the code
    more readable, and provide a single place to redirect writes if needed.
    :param b: The byte to print.
    """
    os.write(context.stdout.fileno(), b)

# -----------------------------------------------------------------------------

def write_str(s):
    """
    Shorthand function that prints a string to stdout.
    :param s: The string to print.
    """
    write(s.encode('UTF-8'))

# -----------------------------------------------------------------------------

def _read_all_output():
    """
    Reads all the output of a command from the current terminal.
    This works by reading from the TTY until a command prompt is found.
    /!\ The end marker is expected to be the same as the one before the
    command was executed! This means that if the command changes the prompt,
    (ie. cd, etc.) this function will never return!
    :return:
    """
    output = b""
    end_marker = context.active_session.input_driver.last_line.encode("UTF-8")
    while not output.endswith(end_marker):
        output += os.read(context.active_session.master, 4096)
    # The last line of the output should be a new prompt. Exclude it from
    # the output.
    return output[:output.rfind(b"\r\n")].decode("UTF-8")

# -----------------------------------------------------------------------------

def shell_exec(command, print_output=False):
    """
    Executes a command in the shell.
    /!\ Do not run commands that change the prompt (ie. cd, etc.)!
    :param command: The command to run.
    :param print_output: Whether the output of the command should be printed
    to stdout.
    :return: The output of the command.
    """
    os.write(context.active_session.master, ("%s\r" % command).encode("UTF-8"))
    output = _read_all_output()
    if print_output:
        write_str(output + "\r\n")
    return output
