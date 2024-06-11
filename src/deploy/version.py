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

from enum import Enum
from functools import total_ordering


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


@total_ordering  # Auto-implement other comparison functions
class Version:
    def __new__(cls, *args, **kwargs):
        pass

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
        if not isinstance(other, Version):
            return False
        return self._major == other._major and self._minor == other._minor

    def __gt__(self, other):
        if not isinstance(other, Version):
            return False
        if self._major > other._major:
            return True
        return self._minor > other._minor

    def __str__(self) -> str:
        return f"v{self._major}.{self._minor}"


@total_ordering  # Auto-implement other comparison functions
class _VersionPatch(Version):
    def __init__(self, major: int = 1, minor: int = 0, patch: int = 0):
        super().__init__(major, minor)
        self._patch = patch

    def bump(self, bump: Bump, increase: int = 1) -> str:
        if require_non_none(bump) == Bump.PATCH:
            _validate_bump_increase(increase)
            self._patch += increase
            return str(self)
        return super().bump(bump, increase)

    @property
    def patch(self) -> int:
        return self._patch

    def __eq__(self, other) -> bool:
        if not isinstance(other, _VersionPatch) or self._patch != other._patch:
            return False
        return super().__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, _VersionPatch):
            return False
        if super().__gt__(other):
            return True
        return self._patch > other._patch

    def __str__(self) -> str:
        return f"{super().__str__()}.{self._patch}"


@total_ordering  # Auto-implement other comparison functions
class _VersionBuildDC(Version):
    def __init__(self, decorated: Version, build: str):
        super().__init__()  # Essentially ignored -- this object is a facade
        self.__decorated = require_non_none(decorated)
        self._build = require_non_none(build)

    def bump(self, bump: Bump, increase: int = 1) -> str:
        return self.__decorated.bump(bump, increase)

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, _VersionBuildDC) or self._build != other._build:
            return False
        return self.__decorated == other.__decorated

    def __gt__(self, other):
        return self.__decorated > other

    def __str__(self) -> str:
        return f"{str(self.__decorated)}-{self._build}"
