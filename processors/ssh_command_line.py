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
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor
from model.driver.input_api import write_str, LogLevel

class SSHOptions(Processor):
    def apply(self, user_input):
        tokens = user_input.split()
        if tokens[0] == "ssh" and "-T" not in tokens:
            write_str("Notice: automatically adding the -T option to the ssh command!\r\n", LogLevel.WARNING)
            return ProcessorAction.FORWARD, (user_input + " -T")
        return ProcessorAction.FORWARD, user_input

    @staticmethod
    def type():
        return ProcessorType.INPUT


register_processor(SSHOptions)
