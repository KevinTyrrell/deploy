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

from typing import Optional, Any, List, Callable
from io import TextIOWrapper
from threading import Thread

from src.util.util import require_non_none


class Program:
    def __init__(self, command: str, program_name: Optional[str] = None):
        """
        :param command: Name of the command, as if executed on the terminal.
        :param program_name: Formal name of the program.
        """
        if not require_non_none(command):
            raise ValueError("Program executable cannot be empty.")
        if not program_name:
            program_name = command
        self.__command: str = command
        self.__program_name: str = program_name

    def exists(self, required: Optional[bool] = False) -> bool:
        """
        :param required: [Optional] Requires the program to exist, if True.
        :return: True if the program exists in the PATH.
        :raises: RuntimeError if `required` flag set and program does not exist.
        """
        from shutil import which
        prog_exists = which(self.__command) is not None
        if required and not prog_exists:
            raise RuntimeError(f"{self.__program_name} was not found within the"
                               f" PATH. Ensure '{self.__command}'is installed.")
        return prog_exists

    def runnable(self, required: Optional[bool] = False, params: Optional[List[str]] = None) -> bool:
        """
        :param required: [Optional] Requires the program to be runnable, if True.
        :param params: [Optional] Parameters to pass into the program.
        :return: True if the program is not runnable.
        :raises: RuntimeError if `required` flag set and program is not runnable.
        """
        cmd = [self.__command] + (params or list())
        status = subprocess.run(cmd, capture_output=True, text=True)
        prog_runnable = status and status.returncode == 0
        if required and not prog_runnable:
            raise RuntimeError(f"{self.__program_name} was not runnable or"
                               f" DNE. Ensure the program is configured.")
        return prog_runnable

    def execute(self, params: Optional[List[str]] = None,
                stdout_cb: Optional[Callable[[str], None]] = print,
                stderr_cb: Optional[Callable[[str], None]] = print) -> int | Any:
        """
        Runs the program with the specified arguments.

        :param params: [Optional] Arguments to pass into the program.
        :param stdout_cb: [Optional] Callback for stdout stream.
        :param stderr_cb: [Optional] Callback for stderr stream.
        :return: Return code of the process.
        """
        params = [self.__command] + (params or [])
        stdout_cb = stdout_cb if stdout_cb else lambda *__: None
        stderr_cb = stderr_cb if stderr_cb else lambda *__: None
        with subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            def line_reader(pipe: TextIOWrapper, cb: Callable[[str], None]):
                while True:
                    line = pipe.readline()
                    if not line:
                        break
                    cb(line.strip())

            # Separate output of stdout and stderr
            stdout_thread = Thread(target=line_reader, args=(process.stdout, stdout_cb))
            stderr_thread = Thread(target=line_reader, args=(process.stderr, stderr_cb))

            stdout_thread.start()
            stderr_thread.start()
            process.wait()
            stdout_thread.join()
            stderr_thread.join()

            return process.returncode

    def __str__(self) -> str:
        return self.__program_name
