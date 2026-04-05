import sys
import unittest
from unittest import mock

from model.plugin.command import Command


def _import_command_manager():
    sys.modules.pop("commands.command_manager", None)
    with mock.patch("glob.glob", return_value=[]):
        with mock.patch("importlib.import_module"):
            module = __import__("commands.command_manager", fromlist=["*"])
    return module


class ExplodingCommand(Command):
    def __init__(self, *args, **kwargs):
        pass

    def execute(self):
        raise RuntimeError("kaboom")

    @staticmethod
    def regexp():
        return r"^\s*\!boom($| )"

    @staticmethod
    def name():
        return "!boom"

    @staticmethod
    def description():
        return "Explodes for testing."

    @staticmethod
    def usage():
        return "Usage: !boom"


class DuplicateCommand(Command):
    def __init__(self, *args, **kwargs):
        pass

    def execute(self):
        return None

    @staticmethod
    def regexp():
        return r"^\s*\!dupe($| )"

    @staticmethod
    def name():
        return "!dupe"

    @staticmethod
    def description():
        return "Used to verify duplicate registration handling."

    @staticmethod
    def usage():
        return "Usage: !dupe"


class TestCommandManager(unittest.TestCase):
    def test_duplicate_registration_remains_stable(self):
        command_manager = _import_command_manager()
        with mock.patch.object(command_manager, "COMMAND_LIST", set()) as command_list:
            with mock.patch.object(command_manager, "write_str") as write_str:
                command_manager.register_plugin(DuplicateCommand)
                command_manager.register_plugin(DuplicateCommand)

        self.assertEqual(command_list, {DuplicateCommand})
        write_str.assert_called_once()
        self.assertIn("Tried to register", write_str.call_args.args[0])

    def test_command_execution_error_mentions_command_identity(self):
        command_manager = _import_command_manager()
        with mock.patch.object(
            command_manager, "COMMAND_LIST", {ExplodingCommand}
        ), mock.patch.object(command_manager, "write_str") as write_str:
            self.assertTrue(command_manager.parse_commands("!boom"))

        messages = [call.args[0] for call in write_str.call_args_list]
        self.assertTrue(
            any("Command !boom (ExplodingCommand) failed with error: kaboom" in msg for msg in messages)
        )

    def test_invalid_list_tag_uses_usage_without_crashing(self):
        command_manager = _import_command_manager()
        with mock.patch.object(
            command_manager, "COMMAND_LIST", {command_manager.ListPlugins}
        ):
            with mock.patch.object(command_manager.ListPlugins, "usage") as usage:
                self.assertTrue(command_manager.parse_commands("!list bogus"))

        usage.assert_called_once()

