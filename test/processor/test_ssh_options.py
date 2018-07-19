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
import processors.ssh_command_line as ssh_command_line
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

    def test_username_standard(self):
        cmdline = "ssh host -p2222 -v"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_username_complex(self):
        cmdline = "echo ls |ssh host -p2222 -v ; echo 'Done!'&"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_username_l_option(self):
        cmdline = "echo ls |ssh host -p2222 -v -T -lroot ; echo 'Done!'&"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)

    def test_username_l_option_2(self):
        cmdline = "echo ls |ssh host -p2222 -v -T -l user ; echo 'Done!'&"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)

    def test_username_not_applicable(self):
        cmdline = "find . -name ls |base64"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)

    def test_T_option_config_bypass(self):
        old = ssh_command_line.context.config["SSHOptions"]["force_disable_pty_allocation"]
        ssh_command_line.context.config["SSHOptions"]["force_disable_pty_allocation"] = False
        cmdline = "ssh root@host -p2222 -v"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)
        ssh_command_line.context.config["SSHOptions"]["force_disable_pty_allocation"] = old

    def test_username_config_bypass(self):
        old = ssh_command_line.context.config["SSHOptions"]["require_explicit_username"]
        ssh_command_line.context.config["SSHOptions"]["require_explicit_username"] = False
        cmdline = "ssh host -p2222 -v"
        p = SSHOptions()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline + " -T")
        ssh_command_line.context.config["SSHOptions"]["require_explicit_username"] = old
