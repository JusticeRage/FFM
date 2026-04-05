import sys
import unittest
from unittest import mock

import processors.processor_manager as processor_manager


def _import_command_manager(files):
    sys.modules.pop("commands.command_manager", None)
    with mock.patch("glob.glob", return_value=files):
        with mock.patch("importlib.import_module") as import_module:
            module = __import__("commands.command_manager", fromlist=["*"])
    return module, import_module


class TestModuleLoading(unittest.TestCase):
    def test_command_modules_load_once(self):
        command_manager, import_module = _import_command_manager(["a.py", "b.py"])

        command_manager._load_command_modules()
        command_manager._load_command_modules()

        self.assertEqual(import_module.call_count, 2)

    def test_command_loader_imports_only_intended_command_files(self):
        command_manager, import_module = _import_command_manager(
            [
                "/tmp/commands/__init__.py",
                "/tmp/commands/command_manager.py",
                "/tmp/commands/enumeration_commands.py",
                "/tmp/commands/help_commands.py",
                "/tmp/commands/replacement_commands.py",
                "/tmp/commands/stealth_commands.py",
            ]
        )

        imported = [call.args[0] for call in import_module.call_args_list]
        self.assertEqual(
            imported,
            [
                "commands.enumeration_commands",
                "commands.help_commands",
                "commands.stealth_commands",
            ],
        )

    def test_processor_modules_load_once(self):
        with mock.patch.object(
            processor_manager.glob, "glob", return_value=["a.py", "b.py"]
        ):
            with mock.patch.object(
                processor_manager.importlib, "import_module"
            ) as import_module:
                processor_manager._processors_loaded = False
                processor_manager._load_processor_modules()
                processor_manager._load_processor_modules()

        self.assertEqual(import_module.call_count, 2)
