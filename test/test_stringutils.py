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
from misc.stringutils import *


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
