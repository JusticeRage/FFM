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
import model.driver.input_api as input_api

class DummyContext:
    def __init__(self):
        self.stdout = open("/dev/null", "w")

    def __del__(self):
        self.stdout.close()

class ProcessorUnitTest(unittest.TestCase):
    """
    This Fixture makes sure that a dummy context is set up, pointing to /dev/null.
    It prevents the tests from crashing when trying to write to stdout.
    """
    def setUp(self):
        self.old_ctx = input_api.context
        input_api.context = DummyContext()

    def tearDown(self):
        input_api.context = self.old_ctx