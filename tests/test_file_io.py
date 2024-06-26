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

from src.deploy.version import Version, Bump, VersionSerializer


class TestFileIO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_file_1(self):
        from pathlib import Path
        dir_path = Path(__file__).parent.parent
        self.assertTrue(dir_path.exists())
        file_path = dir_path.joinpath("Version.ser")
        ser = VersionSerializer(str(dir_path))
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
            file_path.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
