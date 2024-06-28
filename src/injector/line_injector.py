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

from typing import List
from abc import ABC, abstractmethod
from pathlib import Path

from util.util import require_non_none


class LineInjector(ABC):
    @abstractmethod
    def _substitute(self, line: str) -> str:
        """
        Substitutes content into the specified line.

        Line endings and carriage returns should likely be left in place, if present.

        :param line: Line of text from a file, in candidacy for substitution.
        :return: Substituted line of text.
        """
        pass

    @abstractmethod
    def marker(self) -> str:
        """
        Indicates a marker line to search for in the specified file(s), used for injection.

        The injected content will be substituted on the line directly below the marker.

        :return: Marker string in which the injector searches for in the file.
        :raise: FileNotFoundError if specified file DNE.
        """
        pass

    def __parse_file(self, lines: List[str]) -> bool:
        marker = require_non_none(self.marker())
        i, num_lines, changed = 1, len(lines), False
        while i < num_lines:
            if marker in lines[i - 1]:  # Check the line above for the marker.
                # Ask the subclass how to inject content into the line.
                lines[i] = require_non_none(self._substitute(lines[i]))
                i, changed = i + 1, True  # Skip an extra line.
            i += 1
        return changed

    def inject(self, path: str) -> None:
        """
        Injects a modification into a line of a specified file.

        The line to be modified is designated by a marker on the line above.
        If no marker is found in the file, a runtime exception is raised.

        :param path: Path to the specified file.
        """
        file_path = Path(require_non_none(path))
        if not file_path.is_file():
            raise FileNotFoundError(f"Path does not not specify a valid file: {file_path}")
        with open(path, "r+") as file:
            lines = file.readlines()
            if not self.__parse_file(lines):
                raise RuntimeError(f"File \"{file_path.absolute()}\" does not contain expected marker: {self.marker()}")
            file.seek(0)
            file.truncate()
            file.writelines(lines)
