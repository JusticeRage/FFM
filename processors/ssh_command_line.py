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

import re

from model import context
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel
from misc.string_utils import get_commands, get_arguments, CMDLINE_SEPARATORS

class SSHOptions(Processor):
    """
    This processor makes sure that the -T option is present for ssh connections.
    This limits the amount of forensics evidence created and avoids conflicts between
    the remote TTY and the one emulated by FFM.
    """

    def apply(self, user_input):
        # Add the proxy commands to the tokens: torify ssh is considered to be an SSH call.
        separators = CMDLINE_SEPARATORS + tuple(context.config["AssertTorify"]["proxy_commands"].split())
        if "ssh" not in get_commands(user_input, separators=separators):
            return ProcessorAction.FORWARD, user_input

        ssh_cmdline = get_arguments(user_input, "ssh")

        # Block the command if the username is leaking
        if context.config["SSHOptions"]["require_explicit_username"]:
            if "@" not in ssh_cmdline:
                write_str("FFM blocked a command that may leak your local username. "
                          "Please specify the remote user explicitly.\r\n", LogLevel.ERROR)
                return ProcessorAction.CANCEL, None

        # Add the -T option if it is missing
        if context.config["SSHOptions"]["force_disable_pty_allocation"]:
            if not re.search(r'\-[a-zA-Z]*T', ssh_cmdline):  # Check if the -T option is present
                write_str("Notice: automatically adding the -T option to the ssh command!\r\n", LogLevel.WARNING)
                return ProcessorAction.FORWARD, (user_input.replace(ssh_cmdline, "%s %s" % (ssh_cmdline, "-T"), 1))
            return ProcessorAction.FORWARD, user_input

        # Nothing done
        return ProcessorAction.FORWARD, user_input

    @staticmethod
    def type():
        return ProcessorType.INPUT


register_processor(SSHOptions)
