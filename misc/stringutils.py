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
    return s[index:].lstrip()
