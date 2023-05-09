"""
    FFM by @JusticeRage and @ice-wzl

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

from model import context
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel
from misc.string_utils import get_commands, get_arguments, CMDLINE_SEPARATORS
from misc.silent_argparse import SilentArgumentParser

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
        options_added = []

        # Use argparse to look for the interesting arguments in the SSH command:
        parser = SilentArgumentParser()
        parser.add_argument("-l", nargs='?', default=None)
        parser.add_argument("-T", action="store_true")
        parser.add_argument("-o", action="append")
        parser.add_argument("-i", action="append")
        parser.add_argument("-v", action="store_true")
        parser.add_argument("-N", action="store_true")
        parser.add_argument("-D")
        parser.add_argument("-L")
        parser.add_argument("-R")
        parser.add_argument("positional", nargs='+')
        try:
            args, _ = parser.parse_known_args(ssh_cmdline.split())
        except RuntimeError:
            # The SSH command line seems invalid. Let SSH display its error message / usage.
            return ProcessorAction.FORWARD, user_input

        # Block the command if the username is leaking
        if context.config["SSHOptions"]["require_explicit_username"]:
            if not any("@" in arg for arg in args.positional) and not args.l:
                write_str("FFM blocked a command that may leak your local username. "
                          "Please specify the remote user explicitly.\r\n", LogLevel.ERROR)
                return ProcessorAction.CANCEL, None

        # Add -oPubkeyAuthentication=no to prevent SSH keys from leaking.
        if context.config["SSHOptions"]["prevent_ssh_key_leaks"]:
            if not args.i and (
                    not args.o or
                    not any("PubkeyAuthentication" in option for option in args.o)
            ):
                options_added.append("-oPubkeyAuthentication=no")

        # Add -oUserKnownHostsFile=/dev/null to prevent the connexion from being logged there.
        if context.config["SSHOptions"]["disable_known_hosts"]:
            if not args.o or not any("UserKnownHostsFile" in option for option in args.o):
                options_added.append("-oUserKnownHostsFile=/dev/null")

        # Add the -T option if it is missing
        if context.config["SSHOptions"]["force_disable_pty_allocation"]:
            if not args.T:
                options_added.append("-T")

        if context.config["SSHOptions"]["strict_host_key_checking"]:
            if not args.o or not any("StrictHostKeyChecking" in option for option in args.o):
                options_added.append("-oStrictHostKeyChecking=no")

        if options_added:
            user_input = user_input.replace(ssh_cmdline, "%s %s" % (ssh_cmdline, " ".join(options_added)), 1)
            write_str("Notice: the following options were added to the SSH command: %s.\r\n" % ", ".join(options_added),
                      LogLevel.WARNING)
        return ProcessorAction.FORWARD, user_input

    @staticmethod
    def type():
        return ProcessorType.INPUT


register_processor(SSHOptions)
