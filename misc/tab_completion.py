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
        return None, possible[0][len(current_word):]

    # Check whether partial completion can be applied.
    prefix = os.path.commonprefix(possible)
    if prefix:
        return possible, prefix[len(current_word):]
    else:
        return possible, None
