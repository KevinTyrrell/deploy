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

import unittest
from datetime import datetime
from pathlib import Path
from typing import List

from src.deploy.version import Version, Bump, VersionSerializer
from src.injector.version_injector import VersionInjector
from src.injector.date_injector import DateInjector


class TestFileIO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = Path(__file__).parent

    @classmethod
    def tearDownClass(cls):
        pass

    def clear_files(self):
        self.version_path.unlink(missing_ok=True)
        self.sample1_path.unlink(missing_ok=True)

    def setUp(self):
        self.assertTrue(self.dir_path.exists())
        self.version_path = self.dir_path.joinpath("Version.ser")
        self.sample1_path = self.dir_path.joinpath("Sample1Test.txt")
        self.clear_files()

    def tearDown(self):
        self.clear_files()

    @staticmethod
    def write_file(path: Path, content: List[str]) -> List[str]:
        with path.open("w", encoding="utf-8") as file:
            file.writelines(content)
        return content

    def test_file_1(self):
        ser = VersionSerializer(str(self.dir_path))
        examples = ["2.9.1-beta", "505.09.1", "5.0-alpha", "1.0"]
        for ver_str in examples:
            ver = Version(ver_str)
            ser.save(ver)
            self.assertTrue(ser.loadable())
            loaded = ser.load()
            self.assertEqual(loaded, ver)
            loaded.bump(Bump.MAJOR)
            self.assertNotEqual(loaded, ver)
            loaded.bump(Bump.PATCH)

    def test_file_2(self):
        content = self.write_file(self.sample1_path, [
            "/-- DO NOT MODIFY /--/ [deploy Version Marker] --/\n",
            "local version = \"v2.4.1\""
        ])
        version = Version("v9.99.999")
        injector = VersionInjector(version)
        injector.inject(str(self.sample1_path))
        with self.sample1_path.open("r") as file:
            lines = file.readlines()
            self.assertEqual(lines[0], content[0])
            self.assertEqual(lines[1], "local version = \"v9.99.999\"")

    def test_file_3(self):
        content = self.write_file(self.sample1_path, [
            "\n",
            "from tests import testing\n",
            "\n",
            "class Version:\n",
            "\t# /-- DO NOT MODIFY /--/ [deploy Version Marker] --/\n",
            "\tVERSION_STR = 'v34.009.1-alpha'.replace('$','~')\n",
            "\n",
        ])
        version = Version("v22.0.0-batch")
        injector = VersionInjector(version)
        injector.inject(str(self.sample1_path))
        with self.sample1_path.open("r") as file:
            lines = file.readlines()
            self.assertEqual(len(lines), 7)
            self.assertEqual(lines[5], "\tVERSION_STR = 'v22.0.0-batch'.replace('$','~')\n")
            del lines[5]
            del content[5]
            self.assertListEqual(content, lines)

    def test_time_str_package(self):
        from dateutil.parser import parse as parse_date
        test_str = "I will be available on 2024-09-13 in the evening"
        t: datetime | tuple = parse_date(test_str, fuzzy_with_tokens=True)
        self.assertIsNotNone(t)
        self.assertIsInstance(t, tuple)
        self.assertGreater(len(t), 1)
        tokens = t[1]
        self.assertIsNotNone(tokens)
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], "I will be available on ")
        self.assertEqual(tokens[1], " in the evening")

    def test_date_inject_1(self):
        content = self.write_file(self.sample1_path, [
            "from math import exp\n",
            "\n",
            "\n",
            "# Mark: /-- DO NOT MODIFY /--/ [deploy Date Marker] --/\n",
            # "# Compiled on 2023-09-24 -- Python 3.10.9\n",
            "Built on 2023-09-24 See link on GitHub\n",
            "\n",
            "def main():\n",
            "\tpass\n",
            "\n"
        ])
        dt = datetime(2024, 3, 15)
        injector = DateInjector(dt)
        injector.inject(str(self.sample1_path))
        content[4] = "# Compiled on 2024-03-15 -- Python 3.10.9\n"
        with self.sample1_path.open("r") as file:
            lines = file.readlines()
            self.assertListEqual(content, lines)


if __name__ == '__main__':
    unittest.main()
