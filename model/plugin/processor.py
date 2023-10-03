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
from abc import abstractmethod, ABCMeta
from enum import Enum

# -----------------------------------------------------------------------------


class ProcessorType(Enum):
    INPUT = 1
    OUTPUT = 2


# -----------------------------------------------------------------------------


class ProcessorAction(Enum):
    """
    These values are used as return values for the processors.
    FORWARD: Forward the data to other plugins for further processing.
    STOP_PROCESSING: Stop processing the data and use it as is.
    CANCEL: Stop processing the data and do not use it (i.e. don't run the
    command typed by the user, or don't display the output).
    """

    FORWARD = 1
    STOP_PROCESSING = 2
    CANCEL = 3


# -----------------------------------------------------------------------------


class Processor(metaclass=ABCMeta):
    @abstractmethod
    def apply(self, user_input):
        raise NotImplementedError("Method execute is not implemented")

    @staticmethod
    @abstractmethod
    def type():
        raise NotImplementedError("Method type is not implemented")
