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

from model import context
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel
from misc.string_utils import get_commands, get_arguments, CMDLINE_SEPARATORS
from misc.silent_argparse import SilentArgumentParser

class RdesktopOptions(Processor):
    """
    This processor makes sure that the -U option is present for rdesktop connections.
    This makes sure that the current username will not leak.
    """
    def apply(self, user_input):
        # Add the proxy commands to the tokens: torify rdesktop is considered to be a rdesktop call.
        separators = CMDLINE_SEPARATORS + tuple(context.config["AssertTorify"]["proxy_commands"].split())
        if "rdesktop" not in get_commands(user_input, separators=separators):
            return ProcessorAction.FORWARD, user_input

        rdesktop_cmdline = get_arguments(user_input, "rdesktop")

        # Use argparse to look for the interesting arguments in the rdesktop command:
        parser = SilentArgumentParser()
        parser.add_argument("-u")
        try:
            args, _ = parser.parse_known_args(rdesktop_cmdline.split())
        except RuntimeError:
            # The rdesktop command line seems invalid. Let SSH display its error message / usage.
            return ProcessorAction.FORWARD, user_input

        # Block the command if the username is leaking
        if context.config["RdesktopOptions"]["require_explicit_username"]:
            if not args.u:
                write_str("FFM blocked a command that may leak your local username. "
                          "Please specify the remote user explicitly with the -u option.\r\n", LogLevel.ERROR)
                return ProcessorAction.CANCEL, None
        return ProcessorAction.FORWARD, user_input

    @staticmethod
    def type():
        return ProcessorType.INPUT


register_processor(RdesktopOptions)
