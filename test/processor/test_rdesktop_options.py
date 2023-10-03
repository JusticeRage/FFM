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
import processors.rdesktop_command_line as rdesktop_command_line
from processors.rdesktop_command_line import RdesktopOptions
from processors.processor_manager import ProcessorAction
from test.fixture.dummy_context import DummyContextTest


class TestRdesktopCommandLineProcessor(DummyContextTest):
    def test_option_config_bypass(self):
        old = rdesktop_command_line.context.config["RdesktopOptions"][
            "require_explicit_username"
        ]
        rdesktop_command_line.context.config["RdesktopOptions"][
            "require_explicit_username"
        ] = False
        cmdline = "rdesktop 1.2.3.4"
        p = RdesktopOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)

    def test_standard_case(self):
        cmdline = "rdesktop 1.2.3.4"
        p = RdesktopOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)

    def test_standard_case_2(self):
        cmdline = "rdesktop -u Administrator 1.2.3.4"
        p = RdesktopOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
