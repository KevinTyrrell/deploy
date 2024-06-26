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

from re import match

from line_injector import LineInjector
from src.deploy.version import Version
from src.util.util import require_non_none


class VersionInjector(LineInjector):
    # Marker used to designate where injections are to take place in files.
    DEFAULT_VERSION_MARKER = "/-- DO NOT MODIFY /--/ [deploy Version Marker] --/"

    __VERSION_STRING_PATTERNS = [  # Order matters -- by complexity
        r"(.*?)v\d+\.\d+\.\d+\-[a-zA-Z0-9]+(.*)",  # e.g. v2.09.01-alpha
        r"(.*?)v\d+\.\d+\-[a-zA-Z0-9]+(.*)",  # e.g. v1.0-beta
        r"(.*?)v\d+\.\d+\.\d+(.*)",  # e.g. v99.999.9
        r"(.*?)v\d+\.\d+(.*)",  # e.g. v1.0
    ]

    def __init__(self, version: Version, marker: str = DEFAULT_VERSION_MARKER):
        """
        :param version: Version instance to be injected into files.
        :param marker: Marker string to search for in files.
        """
        self.__version = require_non_none(version)
        self.__marker = require_non_none(marker)

    def _substitute(self, line: str) -> str:
        for pattern in self.__VERSION_STRING_PATTERNS:
            matcher = match(pattern, line)
            if matcher:
                return f"{matcher.group(1)}{str(self.__version)}{matcher.group(2)}"
        raise RuntimeError(f"No valid version pattern found in line under Version marker: {line}")

    def marker(self) -> str:
        return self.__marker
