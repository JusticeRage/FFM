# coding=utf-8
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
import re

# Not alphanum in the strictest sense. This list is used to figure out where the cursor
# should jump to when the user presses ^Left or ^Right. There are probably characters
# missing.
alphanum = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéèàùäïöüÿ"

# -----------------------------------------------------------------------------

def find_first_of(s, chars):
    """
    Finds the first instance of a char from a list in the given string.
    :param s: The string into which the characters should be searched.
    :param chars: The group of characters to look for.
    :return: The index of the first matching character in the string, or -1.
    """
    for index, c in enumerate(s):
        if c in chars:
            return index
    return -1

# -----------------------------------------------------------------------------

def find_first_not_of(s, chars):
    """
    Finds the first instance of a char not a given list in a string.
    :param s: The string into which the characters should be searched.
    :param chars: The group of characters to exclude.
    :return: The index of the first character in the string but not in the list, or -1.
    """
    for index, c in enumerate(s):
        if c not in chars:
            return index
    return -1

# -----------------------------------------------------------------------------

def find_last_of(s, chars):
    """
    Finds the last instance of a char from the given group in a string.
    :param s: The string to search.
    :param chars: The group of characters to look for.
    :return: The index of the last matching character in the string, or -1.
    """
    for i in range(0, len(s)):
        index = len(s) - i - 1
        if s[len(s) - i - 1] in chars:
            return index
    return -1

# -----------------------------------------------------------------------------

def find_last_not_of(s, chars):
    """
    Finds the last instance of a char in a string which is not in the given group.
    :param s: The string to search.
    :param chars: The group of characters to exclude.
    :return: The index of the last matching character in the string, or -1.
    """
    for i in range(0, len(s)):
        index = len(s) - i - 1
        if s[len(s) - i - 1] not in chars:
            return index
    return -1

# -----------------------------------------------------------------------------

def get_last_word(s, boundary=' '):
    """
    Returns the last word contained in a string.
    :param s: The string whose last word we want.
    :param boundary: The characters which delimit word boundaries.
    :return:
    """
    # TODO: check if we're in an escaped sequence (open quotes)
    if not s:
        return ""
    if s[-1] in boundary:
        return ""
    index = find_last_of(s, boundary)
    if index != -1:
        return s[index+1:]
    else:
        return s

# -----------------------------------------------------------------------------

def strip(s, strings):
    """
    Standard strip function, but for whole strings instead of chars.
    Note that the strings are each evaluated in order and only tested once.
    :param s: The string to strip.
    :param strings: The strings to remove (both at the front and at the end).
    :return: The stripped string.
    """
    if not strings or not s:
        return s
    for str in strings:
        if len(s) == 1:
            s.strip(str)
        else:
            if s.startswith(str):
                s = s[len(str):]
            if s.endswith(str):
                s = s[:-len(str)]
    return s

# -----------------------------------------------------------------------------

CMDLINE_SEPARATORS = ("|", ";", "&&", "&")

def get_commands(command_line, separators=CMDLINE_SEPARATORS):
    """
    This function splits a command line to return a list of invoked programs
    without their arguments.
    Example: "cat file ; echo "aaa" | less" -> ["cat", "echo", "less"]
    :param command_line: The command line to parse.
    :param separators: The separators that are used to delimit commands.
    "`" is excluded from the default list because in the case of
    "ls `echo -l` -a", items placed after the second ̀ may be other arguments.
    Instead it is handled separately.
    :return: A list of commands contained in the command line
    """
    # Normalize the string. We want to add spaces around separators in case
    # we receive input such as "command1&&command2;command3".
    for s in separators:
        command_line = re.sub(r'%s' % re.escape(s), " %s " % s, command_line)

    tokens = command_line.split()

    # Skip any separator which may be prepended to the command
    while tokens[0] in separators:
        tokens.pop(0)

    # Figure out which tokens are commands and which ones are arguments. We assume that the
    # commands are the first token and all the ones located after a separator.
    commands = [tokens[0]]
    if len(tokens) == 1:
        return commands
    for i in range(1, len(tokens)):
        if tokens[i].startswith("`"):
            commands.append(tokens[i].strip("`"))
        for s in separators:
            if s == tokens[i] and i < len(tokens) - 1 and not tokens[i+1] in separators:
                # The current token is a separator
                commands.append(tokens[i+1])
                i += 1  # Skip the next token as it was already added
                break   # No need to test for other separators, we found one.

    return commands

# -----------------------------------------------------------------------------

def get_arguments(user_input, command):
    """
    This function is used to retrieve the arguments of a specific command in
    a command line. This can be useful if the command line is composed of
    several commands, such as "command1 -A -B ; command2 -C | less". In which
    case, get_arguments can return either "-A -B", "-C" or "" depending
    on the command we're interested in.
    Note that this function will fail if the same command is present multiple
    times in the input (only the first occurrence will be used).

    :param user_input: The command line to parse.
    :param command: The command whose arguments we are interested in.
    :return: A list of arguments that the user is passing to the command.
    """
    cmd_pos = user_input.find(command)
    if cmd_pos == -1:
        return ""
    cmdline = user_input[cmd_pos + len(command):]
    pos = find_first_of(cmdline, ("|;&"))
    if pos != -1:
        cmdline = cmdline[:pos]
    return cmdline.strip()
