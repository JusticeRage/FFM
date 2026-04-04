import unittest
from unittest import mock

import commands.command_manager as command_manager
import processors.processor_manager as processor_manager


class TestModuleLoading(unittest.TestCase):
    def test_command_modules_load_once(self):
        with mock.patch.object(command_manager.glob, "glob", return_value=["a.py", "b.py"]):
            with mock.patch.object(command_manager.importlib, "import_module") as import_module:
                command_manager._commands_loaded = False
                command_manager._load_command_modules()
                command_manager._load_command_modules()

        self.assertEqual(import_module.call_count, 2)

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
