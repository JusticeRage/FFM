import re
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel
from misc.string_utils import get_commands, get_arguments, CMDLINE_SEPARATORS

from processors.assert_torify import AssertTorify

class SSHUser(Processor):
    """
    This processor makes sure that a user was specified in the ssh
    command line to avoid sending the username of the local machine.
    """

    @staticmethod
    def type():
        return ProcessorType.INPUT

    def apply(self, user_input):
        # Check if the ssh connection must be done with the same user as the
        # local one
        if "!user-bypass" in user_input:
            user_input = user_input.replace("!user-bypass", "")
            return ProcessorAction.FORWARD, user_input

        separators = CMDLINE_SEPARATORS + tuple(AssertTorify.PROXY_COMMANDS)
        if "ssh" not in get_commands(user_input, separators=separators):
            return ProcessorAction.FORWARD, user_input

        ssh_cmdline = get_arguments(user_input, "ssh")
        if not re.search(r'@', ssh_cmdline):
            write_str("FFM blocked a command that may leak your local "
                    "username. Add \"!user-bypass\" to override.\r\n", LogLevel.ERROR)
            return ProcessorAction.CANCEL, None

        return ProcessorAction.FORWARD, user_input

register_processor(SSHUser)
