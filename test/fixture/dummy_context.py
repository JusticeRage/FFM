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
import configparser
import os
import unittest

# Modules to monkey-patch:
import model.driver.input_api as input_api
import processors.assert_torify as assert_torify
import processors.ssh_command_line as ssh_command_line
import commands.command_manager as command_manager
import commands.log_control as log_control
import misc.logging as logging

class DummyContext:
    def __init__(self):
        self.stdout = open("/dev/null", "w")
        self.config = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes=("#", ";"))
        self.config.read(os.path.join(os.path.dirname(__file__), "../../ffm.conf"))
        self.log = None

    def __del__(self):
        self.stdout.close()

class DummyContextTest(unittest.TestCase):
    """
    This fixture makes sure that a dummy context is set up, pointing to /dev/null.
    It prevents the tests from crashing when trying to write to stdout.
    """
    def setUp(self):
        self.old_ctx = input_api.context
        self.context = DummyContext()
        input_api.context = self.context
        assert_torify.context = self.context
        ssh_command_line.context = self.context
        log_control.context = self.context
        logging.context = self.context
        command_manager.context = self.context

    def tearDown(self):
        if self.context.log:
            self.context.log.close()
            self.context.log = None
        input_api.context = self.old_ctx
        assert_torify.context = self.old_ctx
        ssh_command_line.context = self.old_ctx
        log_control.context = self.old_ctx
        logging.context = self.old_ctx
        command_manager.context = self.old_ctx
