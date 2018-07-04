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
from processors.ssh_command_line import SSHOptions
from processors.processor_manager import ProcessorAction
from test.processor.processor_test_fixture import ProcessorUnitTest

class TestSSHCommandLineProcessor(ProcessorUnitTest):
    def test_standard_case(self):
        cmdline = "ssh root@host -p2222 -v"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline + " -T")

    def test_complex_case(self):
        cmdline = "torify ssh root@host -p2222 &"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], "torify ssh root@host -p2222 -T &")

    def test_option_already_present(self):
        cmdline = "ssh root@host -T -p2222 -v"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)

    def test_no_ssh(self):
        cmdline = "ls -l |grep passwords > /tmp/pass"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)

    def test_not_really_ssh(self):
        cmdline = "mv ~/.ssh/id_rsa ssh"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)
