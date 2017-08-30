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
import model.input_driver
import model.context

OUTPUT_FILE_NAME = "test_output.bin"

class TestDriver(unittest.TestCase):
    def setUp(self):
        model.context.stdout = open(OUTPUT_FILE_NAME, "wb")
        self.driver = model.input_driver.DefaultInputDriver()
        self.driver.last_line = "root@hostname:~# "  # len() = 17
        self.output = open(OUTPUT_FILE_NAME, "rb")
        model.context.window_size = [24, 80]

    # -----------------------------------------------------------------------------

    def tearDown(self):
        if model.context.stdout is not None:
            model.context.stdout.close()
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

    def test_backwards_move(self):
        # Simple, same-line cases
        self.driver.input_buffer = "A" * 10
        self.assertEqual(self.driver._backwards_move(0), (0, 0))
        self.assertEqual(self.driver._backwards_move(10), (0, -10))
        self.assertEqual(self.driver._backwards_move(200), (0, -10))
        self.assertEqual(self.driver._backwards_move(2, 5), (0, -2))
        # Multi-line cases
        self.driver.input_buffer = "A" * 160
        self.assertEqual(self.driver._backwards_move(80), (1, 0))
        self.assertEqual(self.driver._backwards_move(90), (1, -10))
        self.assertEqual(self.driver._backwards_move(97), (1, -17))
        self.assertEqual(self.driver._backwards_move(98), (2, 62))
        self.assertEqual(self.driver._backwards_move(159), (2, 1))
        self.assertEqual(self.driver._backwards_move(160), (2, 0))
        # When not starting from the end of the buffer
        self.assertEqual(self.driver._backwards_move(10, 100), (0, -10))
        self.assertEqual(self.driver._backwards_move(1, 63), (1, 79))

    # -----------------------------------------------------------------------------

    def test_forward_move(self):
        # Simple, same-line cases
        self.driver.input_buffer = "A" * 10
        self.driver.cursor_position = 3
        self.assertEqual(self.driver._forward_move(0), (0, 0))
        self.assertEqual(self.driver._forward_move(10, 0), (0, 10))
        self.assertEqual(self.driver._forward_move(10, 7), (0, 3))
        self.assertEqual(self.driver._forward_move(1), (0, 1))
        self.assertEqual(self.driver._forward_move(3), (0, 3))
        self.assertEqual(self.driver._forward_move(4), (0, 3))
        self.assertEqual(self.driver._forward_move(200, 0), (0, 10))
        # Multi-line cases
        self.driver.input_buffer = "A" * 160
        self.assertEqual(self.driver._forward_move(1, 63), (0, 1))
        self.assertEqual(self.driver._forward_move(80, 63), (-1, 0))
        self.assertEqual(self.driver._forward_move(1, 62), (-1, -79))
        self.assertEqual(self.driver._forward_move(159, 1), (-2, -1))
        self.assertEqual(self.driver._forward_move(200, 0), (-2, 0))

    # -----------------------------------------------------------------------------

    def test_forward_word_move(self):
        self.driver.input_buffer = "aaaaaa---aaaaaa-"
        self.driver.go_to_sol()
        self.driver._forward_word_move()
        self.assertEqual(self.driver.cursor_position, 10)
        self.driver._forward_word_move()
        self.assertEqual(self.driver.cursor_position, 1)
        self.driver._forward_word_move()
        self.assertEqual(self.driver.cursor_position, 0)
        self.driver._forward_word_move()
        self.assertEqual(self.driver.cursor_position, 0)

    # -----------------------------------------------------------------------------

    def test_backward_word_move(self):
        self.driver.input_buffer = "-aaaaaa---aaaaaa-"
        self.driver._backwards_word_move()
        self.assertEqual(self.driver.cursor_position, 7)
        self.driver._backwards_word_move()
        self.assertEqual(self.driver.cursor_position, 16)
        self.driver._backwards_word_move()
        self.assertEqual(self.driver.cursor_position, 17)
        self.driver._backwards_word_move()
        self.assertEqual(self.driver.cursor_position, 17)

    # -----------------------------------------------------------------------------

    def _send_input(self, s):
        for c in s:
            self.driver.handle_input(c)
