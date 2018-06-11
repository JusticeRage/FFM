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

import unittest
from misc.string_utils import *


class TestStringUtils(unittest.TestCase):
    def test_find_first_of(self):
        self.assertEqual(find_first_of("abcdef", "a"), 0)
        self.assertEqual(find_first_of("abcdef", "d"), 3)
        self.assertEqual(find_first_of("Aaaaaa", "a"), 1)
        self.assertEqual(find_first_of("abcdef", "z"), -1)

    def test_find_first_not_of(self):
        self.assertEqual(find_first_not_of("abcdef", "a"), 1)
        self.assertEqual(find_first_not_of("aaaaab", "a"), 5)
        self.assertEqual(find_first_not_of("aaaaaa", "a"), -1)

    def test_find_last_of(self):
        self.assertEqual(find_last_of("abcdef", "a"), 0)
        self.assertEqual(find_last_of("abcdef", "b"), 1)
        self.assertEqual(find_last_of("abcdef", "f"), 5)
        self.assertEqual(find_last_of("abcdea", "a"), 5)
        self.assertEqual(find_last_of("abcdef", "g"), -1)
        self.assertEqual(find_last_of("", "a"), -1)

    def test_find_last_not_of(self):
        self.assertEqual(find_last_not_of("abcdef", alphanum), -1)
        self.assertEqual(find_last_not_of("abcde/fé", alphanum), 5)
        self.assertEqual(find_last_not_of("@abcdef", alphanum), 0)
        self.assertEqual(find_last_not_of("@abcd-ef", alphanum), 5)
        self.assertEqual(find_last_not_of("@abcd-ef", alphanum + "-"), 0)
        self.assertEqual(find_last_not_of("", alphanum), -1)

    def test_get_last_word(self):
        self.assertEqual(get_last_word("one two three"), "three")
        self.assertEqual(get_last_word("one two three "), "")
        self.assertEqual(get_last_word(""), "")
        self.assertEqual(get_last_word("/tm", boundary="/"), "tm")

    def test_strip(self):
        self.assertEqual(strip("abcd", ["a", "d"]), "bc")
        self.assertEqual(strip("abcd", ["a", "c"]), "bcd")
        self.assertEqual(strip("abcd", ["efgh"]), "abcd")
        self.assertEqual(strip("", ["ad", "bc"]), "")
        self.assertEqual(strip("abcd", ["abc"]), "d")
        self.assertEqual(strip("abcdefgh", ["efgh"]), "abcd")
        self.assertEqual(strip("abcdefgh", ["abcd", "efgh"]), "")
        self.assertEqual(strip("|less&&", ["|", ";", "&&", "&", "`"]), "less")
        # Warning: strings are evaluated in the order they are given:
        self.assertEqual(strip("abcdefgh", ["ef", "gh"]), "abcdef")
        self.assertEqual(strip("abcdefgh", ["gh", "ef"]), "abcd")

    def test_get_commands(self):
        self.assertEqual(get_commands("ls -a -l -h"), ["ls"])
        self.assertEqual(get_commands("cat -a |less"), ["cat", "less"])
        self.assertEqual(get_commands("command1&&command2;command3"), ["command1", "command2", "command3"])
        self.assertEqual(get_commands("command1&& command2; command3 &"), ["command1", "command2", "command3"])
        self.assertEqual(get_commands("ls `echo -l` -a| less"), ["ls", "echo", "less"])

    def test_get_arguments(self):
        self.assertEqual(get_arguments("ls -a -l -h ", "ls"), "-a -l -h")
        self.assertEqual(get_arguments("cat -a |less", "cat"), "-a")
        self.assertEqual(get_arguments("cat -a |less", "echo"), "")
        self.assertEqual(get_arguments("command1&&command2;command3", "command2"), "")
