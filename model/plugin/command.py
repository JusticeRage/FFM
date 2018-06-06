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


class Command(metaclass=ABCMeta):

    @abstractmethod
    def execute(self):
        raise NotImplementedError("Method execute is not implemented")

    @staticmethod
    @abstractmethod
    def regexp():
        raise NotImplementedError("Method regexp is not implemented")

    @staticmethod
    @abstractmethod
    def name():
        raise NotImplementedError("Method name is not implemented")

    @staticmethod
    @abstractmethod
    def description():
        raise NotImplementedError("Method description is not implemented")
