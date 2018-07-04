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
from processors.processor_manager import ProcessorAction
from processors.assert_torify import AssertTorify
from test.processor.processor_test_fixture import ProcessorUnitTest

class TestAssertTorify(ProcessorUnitTest):
    def test_standard_case(self):
        cmdline = "ssh root@host -p2222 -v"
        p = AssertTorify()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_complex_case(self):
        cmdline = "echo ls |nc -vv 10.10.0.1 7777 ; echo 'Done!'"
        p = AssertTorify()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_bypass(self):
        cmdline = "ssh root@host !bypass -p2222 -v"
        p = AssertTorify()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], "ssh root@host  -p2222 -v")

        cmdline = "ssh root@host -p2222 -v !bypass"
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], "ssh root@host -p2222 -v ")

    def test_not_applicable(self):
        cmdline = "find . -name ls |base64"
        p = AssertTorify()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)
