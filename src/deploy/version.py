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

from __future__ import  annotations
from enum import Enum
from functools import total_ordering
from re import match
from pathlib import Path

import pickle


from util.util import require_non_none


class Bump(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

    @staticmethod
    def from_str(bump: str):
        """
        :param bump: String to map to a bump instance.
        :return: Bump instance corresponding to the string, or None.
        """
        try:
            return Bump[require_non_none(bump).upper()]  # Case-insensitive mapping
        except KeyError:
            return None


def _validate_bump_increase(increase: int):
    if increase < 1:
        raise ValueError(f"Version bump increase must be positive: {increase}")


class Version:
    def __new__(cls, version: str):
        """
        Creates a version instance from a semantic versioned string

        The following are examples of semantic versioning:
        v1.12.1     2.0     33.5.09-release         1.0-beta

        :param version: Semantic versioned string
        """
        matcher = match(r".*?(\d+)\.(\d+).*", require_non_none(version))
        if matcher:  # String is, at-minimum, semantic versioned
            major, minor = map(int, matcher.groups())
            matcher = match(r".*?\d+\.\d+\.(\d+).*", version)
            if matcher:  # String includes a 'patch'
                instance = _VersionPatch(major, minor, int(matcher.group(1)))
            else:
                instance = _Version(major, minor)
            matcher = match(r".*\d+\.\d+(\.\d+)?-(.+)", version)
            if matcher:  # String includes a 'build' tag, use decorator
                return _VersionBuildDC(instance, matcher.group(2))
            return instance
        else:
            raise ValueError(f"Version string is not of semantic versioning format: {version}")

    @staticmethod
    def from_path(path: str) -> Version:
        pass


class VersionSerializer:
    __FILE_EXT = "ser"
    __FILE_NAME = "Version"

    def __init__(self, path: str, file_name: str = __FILE_NAME, file_ext: str = __FILE_EXT):
        """
        :param path: Directory path to which the Version is de/serialized to/from.
        :param file_name: Name of the file, omitting extension.
        :param file_ext: Name of the file extension, omitting a dot.
        """
        file = f"{require_non_none(file_name)}.{require_non_none(file_ext)}"
        self.__dir = Path(require_non_none(path))
        self.__file = self.__dir.joinpath(file)

    def loadable(self) -> bool:
        """
        :return: True if the Version can be de-serialized from the path.
        """
        self.__check_valid_dir()
        try:
            self.__check_valid_file()
            return True
        except FileNotFoundError | RuntimeError:
            return False

    def save(self, version: Version) -> None:
        """
        :param version: Version object to be saved to-be serialized.
        """
        self.__check_valid_dir()
        with open(str(self.__file.absolute()), "wb") as file:
            pickle.dump(require_non_none(version), file)

    def load(self) -> Version:
        """
        :return: Attempts to de-serialize the Version object.
        """
        self.__check_valid_dir()
        self.__check_valid_file()
        with open(str(self.__file.absolute()), "rb") as file:
            return pickle.load(file)

    def __check_valid_dir(self) -> None:
        if not self.__dir.exists():
            raise FileNotFoundError(f"Version directory does not exist: {self.__dir}")
        if not self.__dir.is_dir():
            raise RuntimeError(f"Version directory path does not point to a directory: {self.__dir}")

    def __check_valid_file(self) -> None:
        if not self.__file.exists():
            raise FileNotFoundError(f"Version file does not exist: {self.__file}")
        if not self.__file.is_file():
            raise RuntimeError(f"Version file path does not point to a file: {self.__file}")


@total_ordering  # Auto-implement other comparison functions
class _Version:
    def __init__(self, major: int = 1, minor: int = 0):
        self._major: int = major
        self._minor: int = minor

    def bump(self, bump: Bump, increase: int = 1) -> str:
        """
        :param bump: Section of the version to bump up.
        :param increase: Amount to bump the section up by.
        :return: Updated version, in string form.
        :raises: ValueError if increase is non-positive.
        """
        _validate_bump_increase(increase)
        match require_non_none(bump):
            case Bump.MAJOR:
                self._major += increase
                self._minor = 0
            case Bump.MINOR:
                self._minor += increase
        return str(self)

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return 0

    @property
    def build(self) -> str | None:
        return None

    def __eq__(self, other) -> bool:
        if isinstance(other, _Version):
            return self.major == other.major and self.minor == other.minor
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, _Version):
            if self.major > other.major:
                return True
            if self.major < other.major:
                return False
            return self.minor > other.minor
        return NotImplemented

    def __str__(self) -> str:
        return f"v{self._major}.{self._minor}"


@total_ordering  # Auto-implement other comparison functions
class _VersionPatch(_Version):
    def __init__(self, major: int = 1, minor: int = 0, patch: int = 0):
        super().__init__(major, minor)
        self._patch = patch

    def bump(self, bump: Bump, increase: int = 1) -> str:
        if require_non_none(bump) == Bump.PATCH:
            _validate_bump_increase(increase)
            self._patch += increase
            return str(self)
        else:
            self._patch = 0
            return super().bump(bump, increase)

    @property
    def patch(self) -> int:
        return self._patch

    def __eq__(self, other) -> bool:
        match _Version.__eq__(self, other):
            case True:
                if isinstance(other, _VersionPatch):
                    return self.patch == other.patch
                else:
                    return self.patch == 0
            case False:
                return False
        return NotImplemented

    def __gt__(self, other):
        match _Version.__gt__(self, other):
            case True:
                return True
            case False:
                if self.major == other.major and self.minor == other.minor:
                    return self.patch > other.patch
                return False
        return NotImplemented

    def __str__(self) -> str:
        return f"{super().__str__()}.{self._patch}"


@total_ordering  # Auto-implement other comparison functions
class _VersionBuildDC(_Version):
    def __init__(self, decorated: _Version, build: str):
        super().__init__()  # Essentially ignored -- this object is a facade
        self.__decorated = require_non_none(decorated)
        self._build = require_non_none(build)

    def bump(self, bump: Bump, increase: int = 1) -> str:
        self.__decorated.bump(bump, increase)
        return str(self)

    @property
    def major(self) -> int:
        return self.__decorated.major

    @property
    def minor(self) -> int:
        return self.__decorated.minor

    @property
    def patch(self) -> int:
        return self.__decorated.patch

    @property
    def build(self) -> str | None:
        return self._build

    def __eq__(self, other):
        if isinstance(other, _VersionBuildDC):
            return self.__decorated == other.__decorated
        return self.__decorated == other

    def __gt__(self, other):
        if isinstance(other, _VersionBuildDC):
            return self.__decorated > other.__decorated
        return self.__decorated > other

    def __str__(self) -> str:
        return f"{str(self.__decorated)}-{self._build}"
