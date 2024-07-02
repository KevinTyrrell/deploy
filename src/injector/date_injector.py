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

import re
from datetime import datetime
from typing import Tuple, List, TypeVar, Iterable, Deque
from collections import deque

from dateutil.parser import parse as parse_date

from src.injector.line_injector import LineInjector
from src.util.util import require_non_none


class DateInjector(LineInjector):
    # Marker used to designate where injections are to take place in files.
    DEFAULT_VERSION_MARKER = "/-- DO NOT MODIFY /--/ [deploy Date Marker] --/"

    # dateutil.parser._parser.ParserError (ValueError)

    def __init__(self, date: datetime, fmt: str = "%Y-%m-%d", marker: str = DEFAULT_VERSION_MARKER):
        """
        :param date: Date/time instance to be injected into files.
        :param fmt: [Optional] Date format to be used for the injection (default YYYY-MM-DD).
        :param marker: Marker string to search for in files.
        """
        self.__date: str = require_non_none(date).strftime(require_non_none(fmt))
        self.__marker: str = require_non_none(marker)

    def _substitute(self, line: str) -> str:
        parser = _DateParser(line)  # Prepare to find where the date is in the specified string.
        parser.inject_date(self.__date)
        k = parser.rebuild()
        return k

    def marker(self) -> str:
        return self.__marker


class _DateParser:
    __PROTECTED_CHARACTERS = "\n\t\r\f"  # Characters in which dateutil converts erroneously to whitespace
    __STANDARD_TOKEN_PATTERN = f"[{__PROTECTED_CHARACTERS}]+"
    __PROTECTED_TOKEN_PATTERN = f"[^{__PROTECTED_CHARACTERS}]+"
    __TRIM_TOKEN_PATTERN = r"^(\s*)(.*?)(\s*)$"

    def __init__(self, content: str):
        def split_non_empty(pattern: str) -> List[str]:
            return list(filter(lambda s: s != "", re.split(pattern, content)))
        self.__content = require_non_none(content)
        # Control characters are unsafe for dateutil calls. They must be removed ahead of time.
        self.__prot_tokens = split_non_empty(self.__PROTECTED_TOKEN_PATTERN)
        self.__std_tokens = split_non_empty(self.__STANDARD_TOKEN_PATTERN)

    def inject_date(self, date: str) -> None:
        for i in range(len(self.__std_tokens)):
            try:  # parse_date will raise an exception if the token does not contain a date.
                # dateutil also returns whitespace that is part of the date itself (e.g "Jan 16, 2004") -> (' ', ' ').
                # This is a severe problem, as there would be no way to know where that whitespace originated from.
                # Therefore: temporarily trim appended or prepended whitespace, to avoid this issue altogether.
                token, whitespace = self.__trim_token(self.__std_tokens[i])
                _, parts = parse_date(token, fuzzy_with_tokens=True)
                # Given the un-used portions from the parser, reconstruct the string with the injected date.
                prefix, suffix = self.prefix_suffix_from_parts(token, parts)
                token = f"{prefix}{date}{suffix}"
                self.__std_tokens[i] = f"{whitespace[0]}{token}{whitespace[1]}"  # Re-insert the trimmed whitespace.
                return  # Only perform one date injection.
            except ValueError:
                pass  # Skip this portion of the string as it does not contain a date.
        raise ValueError(f"No valid date format was found in marked line: {self.__content}")

    def rebuild(self) -> str:
        prot, std, p_len, s_len = self.__prot_tokens, self.__std_tokens, len(self.__prot_tokens), len(self.__std_tokens)
        if p_len > s_len:
            return ''.join(self.__zipper_merge(prot, std))
        if s_len > p_len:
            return ''.join(self.__zipper_merge(std, prot))
        # std is guaranteed non-empty, as the date is a member.
        if self.__content.startswith(prot[0]):
            return ''.join(self.__zipper_merge(prot, std))
        return ''.join(self.__zipper_merge(std, prot))

    @staticmethod
    def prefix_suffix_from_parts(token: str, parts: Iterable[str]) -> Tuple[str, str]:
        # Locate where the date was in the string, strictly based on un-used string parts.
        source, prefix, suffix = token, "", ""
        deq: Deque[str] = deque(filter(lambda s: s != "", parts))
        while True:
            if not deq:  # Empty protection.
                return prefix, suffix
            part = deq[0]
            if source.startswith(part):
                prefix += deq.popleft()  # Portion is not part of the date.
                source = source[len(part):]  # Remove portion from source.
            else:
                break
        while True:
            if not deq:  # Empty protection.
                return prefix, suffix
            part = deq[-1]
            if source.endswith(part):
                suffix = deq.pop() + suffix  # Portion is not part of the date.
                source = source[:len(part)]  # Remove portion from source.
            else:
                return prefix, suffix

    @classmethod
    def __trim_token(cls, token: str) -> Tuple[str, Tuple[str, str]]:
        matcher = re.match(cls.__TRIM_TOKEN_PATTERN, token)
        # (content, (prefix_whitespace, suffix_whitespace))
        return matcher.group(2), (matcher.group(1), matcher.group(3))

    __T = TypeVar("__T")

    @staticmethod
    def __zipper_merge(a: List[__T], b: List[__T]) -> List[__T]:
        merge = []
        i, j, a_len, b_len = 0, 0, len(a), len(b)
        while i < a_len and j < b_len:
            merge.append(a[i])
            merge.append(b[j])
            i += 1
            j += 1
        merge.extend(a[i:])
        merge.extend(b[j:])
        return merge
