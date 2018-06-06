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

import glob
import os
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from model.driver.input_api import write_str, LogLevel

INPUT_PROCESSOR_LIST = set()
OUTPUT_PROCESSOR_LIST = set()


def register_processor(plugin):
    if not issubclass(plugin, Processor):
        write_str("Tried to register %s which is not a valid command!\r\n" % str(plugin), LogLevel.ERROR)
        return
    if plugin.type() == ProcessorType.INPUT:
        destination = INPUT_PROCESSOR_LIST
    elif plugin.type() == ProcessorType.OUTPUT:
        destination = OUTPUT_PROCESSOR_LIST
    else:
        write_str("The processor's type (%s) is unsupported." % plugin.type())
        return

    if plugin in destination:
        write_str("Tried to register %s twice!\r\n" % str(plugin), LogLevel.ERROR)
        return
    else:
        destination.add(plugin)

# -----------------------------------------------------------------------------

def apply_input_processors(user_input):
    """
    Applies the input processor to the command line which was typed by a user.
    :param user_input: The command line that is about to be passed to the shell.
    :return: Whether the command line should be passed to the underlying shell,
    and the processed command line.
    """
    if not user_input:  # Abort immediately if there is no input.
        return True, user_input

    command_line = user_input
    for p in INPUT_PROCESSOR_LIST:
        processor_instance = p()
        action, command_line = processor_instance.apply(command_line)
        if action == ProcessorAction.FORWARD:
            continue
        elif action == ProcessorAction.STOP_PROCESSING:
            return True, command_line
        elif action == ProcessorAction.CANCEL:
            return False, None
    return True, command_line

# -----------------------------------------------------------------------------
# This section registers all processors at startup.
# -----------------------------------------------------------------------------

# Look for processors in this folder
folder = os.path.dirname(__file__)
for f in glob.glob(os.path.join(folder, "*.py")):
    if f == __file__ or f.endswith("__init__.py"):
        continue
    with open(f, "rb") as fd:
        exec(compile(fd.read(), f, 'exec'))
