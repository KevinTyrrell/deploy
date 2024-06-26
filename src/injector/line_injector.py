"""
    Tool used to create and manage tagged version commits/releases
    Copyright (C) 2024  Kevin Tyrrell

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod


class LineInjector(ABC):
    @abstractmethod
    def _substitute(self, x):
        pass

    @abstractmethod
    def marker(self) -> str:
        """
        Indicates a marker line to search for in the specified file(s), used for injection.

        The injected content will be substituted on the line directly below the marker.

        :return: Marker string in which the injector searches for in the file.
        """
        pass
