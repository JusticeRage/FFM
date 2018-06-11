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
from model.plugin.processor import Processor, ProcessorType, ProcessorAction
from processors.processor_manager import register_processor

class TestOutput(Processor):
    """
    This example processor simply highlights the word "password".
    """

    def apply(self, output):
        output = re.sub(b'password', b"\033[91mpassword\033[0m", output)
        return ProcessorAction.FORWARD, output

    @staticmethod
    def type():
        return ProcessorType.OUTPUT


# Uncomment the following line if you want to enable this processor!
# register_processor(TestOutput)
