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
from commands.command_manager import parse_commands
from model.driver.input_api import write_str
from test.fixture.dummy_context import DummyContextTest


class TestLogCommand(DummyContextTest):
    def test_standard_case(self):
        f = "unittest_ffm.log"
        cmdline = "   !log    %s" % f
        self.assertTrue(parse_commands(cmdline))
        self.assertIsNotNone(self.context.log)
        self.assertEqual(f, self.context.log.name)

        message = "Unit test!"
        write_str(message)

        cmdline = "!log off"
        self.assertTrue(parse_commands(cmdline))
        self.assertIsNone(self.context.log)

        self.assertTrue(os.path.exists(f))
        with open(f, "r") as fd:
            self.assertEqual(message, fd.read())
        os.remove(f)
