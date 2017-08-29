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
import model.driver
import model.context

OUTPUT_FILE_NAME = "test_output.bin"

class TestDriver(unittest.TestCase):
    def setUp(self):
        model.driver.OUTPUT_FILE = open(OUTPUT_FILE_NAME, "wb")
        self.driver = model.driver.DefaultTerminalDriver()
        self.driver.last_line = "root@hostname:~# "  # len() = 17
        self.output = open(OUTPUT_FILE_NAME, "rb")
        model.context.window_size = [24, 80]

    # -----------------------------------------------------------------------------

    def tearDown(self):
        if model.driver.OUTPUT_FILE is not None:
            model.driver.OUTPUT_FILE.close()
        if self.output is not None:
            self.output.close()
        if os.path.exists("test_output.bin"):
            os.remove("test_output.bin")

    # -----------------------------------------------------------------------------

    def test_pop(self):
        self.driver.pop()
        self.assertEqual(self.driver.input_buffer, "")
        self.driver.input_buffer = "123456"
        self.driver.pop()
        self.assertEqual(self.driver.input_buffer, "12345")
        self.driver.pop(3)
        self.assertEqual(self.driver.input_buffer, "12")
        # Tests with the cursor
        self.driver.input_buffer = "123456"
        self.driver.cursor_position = len(self.driver.input_buffer)
        self.driver.pop()
        self.assertEqual(self.driver.input_buffer, "123456")
        self.driver.cursor_position = 2
        self.driver.pop(2)
        self.assertEqual(self.driver.input_buffer, "1256")

    # -----------------------------------------------------------------------------

    def test_handle_input(self):
        self.driver.handle_input("A")
        self.assertEqual(self.driver.input_buffer, "A")
        self.assertEqual(self.output.read(10), b"A")

    # -----------------------------------------------------------------------------

    def test_handle_input_keys(self):
        # Left arrow with an empty buffer.
        self._send_input("\x1B[D")
        self.assertEqual(self.output.read(10), b"")
        # Left arrow with some bytes in the buffer.
        self._send_input("AAA\x1B[D")
        self.assertEqual(self.output.read(10), b"AAA\x1B[D")
        self.assertEqual(self.driver.cursor_position, 1)

    # -----------------------------------------------------------------------------

    def test_end_to_offset(self):
        # Simple, same-line cases
        self.driver.input_buffer = "A" * 10
        x, y = self.driver._end_to_offset(0)
        self.assertEqual([x, y], [0, 0])
        x, y = self.driver._end_to_offset(10)
        self.assertEqual([x, y], [0, -10])
        x, y = self.driver._end_to_offset(200)
        self.assertEqual([x, y], [0, -10])
        # Multi-line cases
        self.driver.input_buffer = "A" * 160
        x, y = self.driver._end_to_offset(80)
        self.assertEqual([x, y], [1, 0])
        x, y = self.driver._end_to_offset(90)
        self.assertEqual([x, y], [1, -10])
        x, y = self.driver._end_to_offset(97)
        self.assertEqual([x, y], [1, -17])
        x, y = self.driver._end_to_offset(98)
        self.assertEqual([x, y], [2, 62])
        x, y = self.driver._end_to_offset(159)
        self.assertEqual([x, y], [2, 1])
        x, y = self.driver._end_to_offset(160)
        self.assertEqual([x, y], [2, 0])

    # -----------------------------------------------------------------------------

    def _send_input(self, s):
        for c in s:
            self.driver.handle_input(c)
