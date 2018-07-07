from processors.processor_manager import ProcessorAction
from processors.ssh_user import SSHUser
from test.processor.processor_test_fixture import ProcessorUnitTest

class TestAssertTorify(ProcessorUnitTest):
    def test_standard_case(self):
        cmdline = "ssh host -p2222 -v"
        p = SSHUser()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_complex_case(self):
        cmdline = "echo ls |ssh host -p2222 -v ; echo 'Done!'&"
        p = SSHUser()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.CANCEL)
        self.assertEqual(result[1], None)

    def test_bypass(self):
        cmdline = "ssh host !user-bypass -p2222 -v"
        p = SSHUser()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], "ssh host  -p2222 -v")

        cmdline = "ssh host -p2222 -v !user-bypass"
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], "ssh host -p2222 -v ")

    def test_not_applicable(self):
        cmdline = "find . -name ls |base64"
        p = SSHUser()
        result = p.apply(cmdline)
        self.assertEqual(result[0], ProcessorAction.FORWARD)
        self.assertEqual(result[1], cmdline)
