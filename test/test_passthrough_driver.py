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
import unittest

import model.context
import model.driver.passthrough

OUTPUT_FILE_NAME = "test_output.bin"

class TestPassthroughDriver(unittest.TestCase):
    def setUp(self):
        model.context.stdout = open(OUTPUT_FILE_NAME, "wb")
        self.driver = model.driver.passthrough.PassthroughDriver(model.context.stdout.fileno())
        self.output = open(OUTPUT_FILE_NAME, "rb")

    def tearDown(self):
        if model.context.stdout is not None:
            model.context.stdout.close()
        if self.output is not None:
            self.output.close()
        if os.path.exists(OUTPUT_FILE_NAME):
            os.remove(OUTPUT_FILE_NAME)

    def test_simple(self):
        self.driver.handle_input(0x41)
        self.assertEqual(self.output.read(100).decode("UTF-8"), "A")
        self.driver.handle_bytes("This is a test!".encode("UTF-8"))
        self.assertEqual(self.output.read(100).decode("UTF-8"), "This is a test!")
        self.driver.handle_bytes(b"\x1B[D")
        self.assertEqual(self.output.read(100), b"\x1B[D")
