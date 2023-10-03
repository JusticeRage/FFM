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

from model.driver.input_api import *
from commands.command_manager import COMMAND_LIST


def complete(current_word, candidates):
    """
    Completes the current word from a list of candidates.
    :param current_word:
    :param candidates:
    :return: Two values: the list of valid autocompletion candidates, and
    a suffix that can safely be applied to the current word before there is
    any ambiguity (i.e if the word is "a" and candidates are ["abc", "abd"],
    the second return value will be "b" as the word can be completed to "ab").
    """
    if len(current_word):
        possible = list(filter(lambda s: s.startswith(current_word), candidates))
    else:
        possible = candidates
    # Easy cases: no possible completion, or only one.
    if len(possible) == 0:
        return None, None
    elif len(possible) == 1:
        return None, possible[0][len(current_word) :]

    # Check whether partial completion can be applied.
    prefix = os.path.commonprefix(possible)
    if prefix:
        return possible, prefix[len(current_word) :]
    else:
        return possible, None


# -----------------------------------------------------------------------------


def remote_completion(base_directory):
    """
    This function returns a list of possible completion candidates by looking
    at the contents of the current directory, through the PTY. It should be
    used by default, as it returns results from the machine currently
    receiving commands.
    :param base_directory: The base directory to search from.
    :return: A list of all the files and folders in the current "path".
    """
    if base_directory:
        output = shell_exec(
            "ls -1A --color=never --indicator-style=slash "
            "-w %d %s 2>/dev/null" % (context.window_size[1], base_directory),
            timeout=30,
        )
    else:
        output = shell_exec(
            "ls -1A --color=never --indicator-style=slash "
            "-w %d 2>/dev/null" % context.window_size[1],
            timeout=30,
        )

    # Add results from the path if needed
    if not base_directory:
        output += "\r\n"
        output += shell_exec(
            "ls -1A --color=never --indicator-style=slash -w %d "
            "`echo $PATH |tr ':' ' '` |grep -ve ':$\|^$' |sort -u "
            "2>/dev/null" % context.window_size[1],
            timeout=30,
        )

    # Add plugins if needed
    if not base_directory:
        output += "\r\n" + "\r\n".join(p.name() for p in COMMAND_LIST)

    return sorted(output.split("\r\n"))


# -----------------------------------------------------------------------------


def local_completion(base_directory):
    """
    This function returns a list of possible completion candidates from the local
    machine (i.e. the one on which FFM is running, which may not be the one that
    currently executes the command - the user may have SSH'd into another one).
    :param base_directory: The base directory to search from.
    :return: A list of all the files and folders in the current "path".
    """
    candidates = set()
    if base_directory:
        base_directory = os.path.expanduser(base_directory)
    for f in os.listdir(base_directory if base_directory else "."):
        if os.path.isdir(os.path.join(base_directory if base_directory else ".", f)):
            candidates.add(f + "/")  # Add a trailing slash to directories
        else:
            candidates.add(f)

    # Also search the PATH if it makes sense in the context:
    if not base_directory:
        try:
            path = os.environ["PATH"]
        except KeyError:
            return candidates
        for p in path.split(":"):
            if p:
                candidates.update(os.listdir(p))

    # Add plugins if needed
    if not base_directory:
        candidates.update(p.name() for p in COMMAND_LIST)

    return sorted(candidates)
