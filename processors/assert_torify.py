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

from model import context
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel
from misc.string_utils import get_commands
from misc.process_utils import get_children


class AssertTorify(Processor):
    """
    This processor makes sure that a select number of network commands are correctly proxied.
    It does its best to ensure that this is only enforced on the local machine.
    """

    def __init__(self):
        self.proxy_commands = context.config["AssertTorify"]["proxy_commands"].split()
        self.network_commands = context.config["AssertTorify"][
            "network_commands"
        ].split()

    def apply(self, user_input):
        # Check if the config allows any meaningful processing
        if not self.proxy_commands or not self.network_commands:
            return ProcessorAction.FORWARD, user_input

        # Check if the user explicitly asked to bypass this check
        if "!bypass" in user_input:
            user_input = user_input.replace(
                "!bypass", ""
            )  # Remove this option from the command line
            return ProcessorAction.FORWARD, user_input

        # Verify if the command is being proxyfied.
        commands = get_commands(user_input)
        for c in self.proxy_commands:
            if (
                c in commands
            ):  # The user remembered to issue a proxy command. All is well.
                return ProcessorAction.FORWARD, user_input

        # The command is not proxified. Should it be?
        for c in self.network_commands:
            if c in commands:  # The command should probably be proxyfied.
                children = get_children()
                for child in children:
                    # There is already a network command running in FFM. This means (for instance) that the user
                    # SSH'd into another machine, in which case there is no risk of leaking the local IP address.
                    if os.path.basename(child) in self.network_commands:
                        return ProcessorAction.FORWARD, user_input

                write_str(
                    'FFM blocked a command which might need to be proxied. Add "!bypass" to the '
                    "command line to override or use:\r\n * "
                    + "\r\n * ".join(self.proxy_commands)
                    + "\r\n",
                    LogLevel.ERROR,
                )
                return ProcessorAction.CANCEL, None

        # No dangerous command was issued, proceed.
        return ProcessorAction.FORWARD, user_input

    @staticmethod
    def type():
        return ProcessorType.INPUT


register_processor(AssertTorify)
