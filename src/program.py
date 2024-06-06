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

import subprocess

from typing import Optional

from util import require_non_none


class Program:
    def __init__(self, command: str, program_name=None):
        """
        :param command: Name of the command, as if executed on the terminal
        :param program_name: Formal name of the program
        """
        if not require_non_none(command):
            raise ValueError("Program executable cannot be empty.")
        if not program_name:
            program_name = command
        self.__command: str = command
        self.__program_name: str = program_name

    def exists(self) -> bool:
        """
        :return: True if the program exists on the PATH
        """
        from shutil import which
        return which(self.__command) is not None

    def runnable(self, *args: Optional[str]) -> bool:
        """
        :param args: [Optional] List of commands to pass into the program ('--version' by default)
        :return: True, if the program can be executed
        """
        params = [self.__command] + list(args or ["--version"])
        status = subprocess.run(params, capture_output=True, text=True)
        return status and hasattr(status, "returncode") and status.returncode == 0

    def check(self) -> None:
        """
        Ensures the program is installed and is runnable
        """
        if not self.exists():
            raise RuntimeError(f"{self.__program_name} was not found\
             within the PATH. Ensure '{self.__command}'is installed.")
        if not self.runnable():
            raise RuntimeError(f"{self.__program_name} was not\
             runnable or DNE. Ensure the program is configured.")

    def __str__(self) -> str:
        return self.__program_name
