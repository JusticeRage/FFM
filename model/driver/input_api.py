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
import shlex
import string
import sys
import time

MARKER_STR = "".join(random.choice(string.ascii_letters) for _ in range(32))
MARKER = MARKER_STR.encode("UTF-8")

WARNING = "\033[93m"
ERROR = "\033[91m"
ENDC = "\033[0m"

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
    write(s.encode("UTF-8"))


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
    misc.logging.log(msg.encode("UTF-8"))
    write_str_internal(msg)


# -----------------------------------------------------------------------------


def shell_quote(value):
    """
    Quotes a string so it can be safely embedded into a shell command.
    :param value: The string to quote.
    :return: A shell-escaped version of the string.
    """
    return shlex.quote(str(value))


def shell_join(values):
    """
    Quotes and joins a sequence of shell arguments.
    :param values: Iterable of argument values.
    :return: A shell-safe command-line fragment.
    """
    return " ".join(shell_quote(value) for value in values)


def _new_marker():
    """
    Generates a marker that is unlikely to appear in command output.
    :return: A random ascii marker as bytes.
    """
    return "".join(random.choice(string.ascii_letters) for _ in range(32)).encode(
        "UTF-8"
    )


def _build_exec_command(command, start_marker, end_marker):
    """
    Wraps a command with explicit begin/end markers so the harness can detect
    completion without relying on the prompt.
    :param command: The command to run.
    :param start_marker: Marker emitted immediately before the command.
    :param end_marker: Marker emitted with the command's exit status.
    :return: A shell command string.
    """
    return (
        "printf '%s\\n' {start}\n"
        "{command}\n"
        "__ffm_status=$?\n"
        "printf '%s:%s\\n' {end} \"$__ffm_status\""
    ).format(
        start=shell_quote(start_marker.decode("UTF-8")),
        command=command,
        end=shell_quote(end_marker.decode("UTF-8")),
    )


def _read_all_output(timeout, start_marker=None, end_marker=None):
    r"""
    Reads all the output of a command from the current terminal.
    When explicit markers are provided, output is collected until the end
    marker is seen and the data between both markers is returned.
    Otherwise, this falls back to reading until the command prompt is found.
    /!\ In prompt-detection mode, the end marker is expected to be the same as
    the one before the command was executed! This means that if the command
    changes the prompt, (ie. cd, etc.) this function will never return!
    :param timeout The maximum amount of time to wait for the end of the
    output.
    :return:
    """
    output = b""
    deadline = time.monotonic() + timeout
    if end_marker is not None:
        start_pattern = (
            re.compile(rb"(?:^|\r?\n)" + re.escape(start_marker) + rb"\r?\n")
            if start_marker
            else None
        )
        end_pattern = re.compile(
            rb"(?:^|\r?\n)" + re.escape(end_marker) + rb":\d+(?:\r?\n|$)"
        )
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                write_str(
                    "Timeout reached; giving up on trying to capture the output.\r\n",
                    LogLevel.ERROR,
                )
                return output.decode("UTF-8")
            r, _, _ = select.select([context.active_session.master], [], [], remaining)
            if context.active_session.master in r:
                output += os.read(context.active_session.master, 4096)
                end_match = end_pattern.search(output)
                if end_match:
                    start_index = 0
                    if start_pattern:
                        start_match = start_pattern.search(output)
                        if not start_match:
                            continue
                        start_index = start_match.end()
                    return (
                        output[start_index : end_match.start()]
                        .rstrip(b"\r\n")
                        .decode("UTF-8")
                    )
            else:
                write_str(
                    "Timeout reached; giving up on trying to capture the output.\r\n",
                    LogLevel.ERROR,
                )
                return output.decode("UTF-8")

    end_marker = context.active_session.input_driver.last_line.encode("UTF-8")
    if not end_marker:
        # No prompt to detect. Add a marker manually to know when to stop reading the output.
        end_marker = MARKER
        os.write(
            context.active_session.master, ("echo -n %s\r" % MARKER_STR).encode("UTF-8")
        )
    # Strip ascii color codes and such when looking for the end marker.
    while not re.sub(rb"\x1b]0;.*?\x07|\x1b\[[0-?]*[ -/]*[@-~]", b"", output).endswith(
        end_marker
    ):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            write_str(
                "Timeout reached; giving up on trying to capture the output.\r\n",
                LogLevel.ERROR,
            )
            return output.decode("UTF-8")
        r, _, _ = select.select([context.active_session.master], [], [], remaining)
        if context.active_session.master in r:
            output += os.read(context.active_session.master, 4096)
        else:
            write_str(
                "Timeout reached; giving up on trying to capture the output.\r\n",
                LogLevel.ERROR,
            )
            return output.decode("UTF-8")

    # The last line of the output should be a new prompt or the marker. Exclude it from
    # the output.
    index = output.rfind(b"\r\n")
    if index != -1:
        return output[:index].decode("UTF-8")
    else:  # No new line in the output: it's only the marker then.
        return ""


# -----------------------------------------------------------------------------


def _stream_output(timeout, output_handler, start_marker, end_marker):
    """
    Streams a command's output from the current terminal to a callback until the
    explicit end marker is found.
    :param timeout: The maximum amount of time to wait.
    :param output_handler: Callback receiving bytes that belong to the command output.
    :param start_marker: Marker emitted immediately before the command output.
    :param end_marker: Marker emitted after the command output with the exit status.
    :return: The command's exit code.
    """
    output = b""
    started = False
    deadline = time.monotonic() + timeout
    start_pattern = re.compile(rb"(?:^|\r?\n)" + re.escape(start_marker) + rb"\r?\n")
    end_pattern = re.compile(
        rb"(?:^|\r?\n)" + re.escape(end_marker) + rb":(\d+)(?:\r?\n|$)"
    )
    retain = len(end_marker) + 64

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            write_str(
                "Timeout reached; giving up on trying to capture the output.\r\n",
                LogLevel.ERROR,
            )
            raise RuntimeError("Timed out while streaming command output.")
        r, _, _ = select.select([context.active_session.master], [], [], remaining)
        if context.active_session.master not in r:
            write_str(
                "Timeout reached; giving up on trying to capture the output.\r\n",
                LogLevel.ERROR,
            )
            raise RuntimeError("Timed out while streaming command output.")

        output += os.read(context.active_session.master, 4096)

        if not started:
            start_match = start_pattern.search(output)
            if not start_match:
                continue
            output = output[start_match.end() :]
            started = True

        end_match = end_pattern.search(output)
        if end_match:
            payload = output[: end_match.start()]
            if payload:
                output_handler(payload)
            return int(end_match.group(1))

        if len(output) > retain:
            output_handler(output[:-retain])
            output = output[-retain:]


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
    r"""
    Executes a command in the shell.
    The command is wrapped with explicit begin/end markers so completion does
    not depend on prompt detection.
    :param command: The command to run.
    :param print_output: Whether the output of the command should be printed
    to stdout.
    :param output_cleaner: A function to call on the output to preprocess it
    before printing it (ex: remove trailing newlines, etc.)
    :param timeout: The maximum time to wait before giving up on trying to
    read the output of the command.
    :return: The output of the command.
    """
    start_marker = _new_marker()
    end_marker = _new_marker()
    pass_command(_build_exec_command(command, start_marker, end_marker))
    output = _read_all_output(timeout, start_marker=start_marker, end_marker=end_marker)
    if output_cleaner and callable(output_cleaner):
        output = output_cleaner(output)
    if print_output and output:
        write_str(output + "\r\n")
    return output


# -----------------------------------------------------------------------------


def shell_exec_stream(command, output_handler, timeout=300):
    """
    Executes a command in the shell and streams its output to a callback.
    :param command: The command to run.
    :param output_handler: Callback receiving byte chunks from stdout/stderr.
    :param timeout: The maximum time to wait for the command to finish.
    :return: The command's exit code.
    """
    start_marker = _new_marker()
    end_marker = _new_marker()
    pass_command(_build_exec_command(command, start_marker, end_marker))
    return _stream_output(timeout, output_handler, start_marker, end_marker)


# -----------------------------------------------------------------------------


def file_exists(path):
    """
    Tests whether a file exists.
    :param path: The path to test.
    :return: True if the file exists, False otherwise.
    """
    output = shell_exec("test -f %s ; echo $?" % shell_quote(path), timeout=30)
    return int(output) == 0


# -----------------------------------------------------------------------------


def is_directory(path):
    """
    Tests whether a given file is a directory.
    :param path: The path to test
    :return: True if the file is a directory.
    """
    output = shell_exec("test -d %s ; echo $?" % shell_quote(path), timeout=30)
    return int(output) == 0


# -----------------------------------------------------------------------------


def check_command_existence(cmd):
    """
    Verifies that a given command exists on the machine.
    :param cmd: The command whose existence we want to check.
    :return: True if the command is present on the system, False otherwise.
    """
    output = shell_exec(
        "command -v %s >/dev/null ; echo $?" % shell_quote(cmd), timeout=30
    )
    return int(output) == 0


# -----------------------------------------------------------------------------


def get_tmpfs_folder():
    """
    Finds a tmpfs directory suitable for most operations. The citeria are:
    - RW permissions
    - The noexec flag is not set.
    :return: A suitable folder, or None if it couldn't be found.
    """
    candidates = shell_exec(
        'mount -t tmpfs |grep "rw" |grep -v "noexec" |cut -d" " -f3', timeout=30
    )
    if candidates:
        return candidates.split("\r\n")[0]
    else:
        return None
