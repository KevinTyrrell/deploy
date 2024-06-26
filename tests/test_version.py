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


class TestVersion(unittest.TestCase):

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

    def test_version_1(self):
        v = Version("v2.9")
        self.assertEqual(str(v), "v2.9")
        v.bump(Bump.MINOR)
        self.assertEqual(v.minor, 10)
        self.assertIsNone(v.build)
        self.assertEqual(v.patch, 0)
        self.assertEqual(v.major, 2)
        self.assertEqual(v.bump(Bump.MAJOR), "v3.0")

    def test_version_2(self):
        v = Version("34.999.5")
        self.assertEqual(v.bump(Bump.PATCH), "v34.999.6")
        self.assertEqual(v.bump(Bump.MINOR), "v34.1000.0")
        self.assertEqual(v.bump(Bump.MAJOR), "v35.0.0")
        self.assertEqual(v.bump(Bump.MINOR), "v35.1.0")
        self.assertEqual(v.bump(Bump.MAJOR, 5), "v40.0.0")

    def test_version_3(self):
        v = Version("v01.12.0001-vanilla")
        self.assertEqual(str(v), "v1.12.1-vanilla")
        self.assertEqual(v.build, "vanilla")
        self.assertEqual(v.bump(Bump.PATCH, 2), "v1.12.3-vanilla")

    def test_version_4(self):
        v1 = Version("9.5")
        v2 = Version("10.0")
        self.assertTrue(v2 > v1)
        v1.bump(Bump.MAJOR)
        self.assertTrue(v1 == v2)

    def test_version_5(self):
        v1 = Version("1.2.3-beta")
        v2 = Version("v1.2.3-alpha")
        self.assertTrue(v1 == v2)
        self.assertFalse(v1 > v2)
        self.assertFalse(v1 < v2)
        v1.bump(Bump.PATCH)
        self.assertTrue(v1 > v2)

    def test_version_6(self):
        v1 = Version("5.0")
        v2 = Version("4.9.1")
        self.assertTrue(v1 > v2)
        self.assertGreater(v1, v2)
        self.assertLess(v2, v1)
        v2.bump(Bump.MAJOR)
        self.assertEqual(v1, v2)
        self.assertEqual(v2, v1)
        v2.bump(Bump.PATCH)
        self.assertGreater(v2, v1)
        self.assertLess(v1, v2)

    def test_version_7(self):
        v1 = Version("23.09.35")
        v2 = Version("23.09.33")
        self.assertGreater(v1, v2)
        self.assertLess(v2, v1)
        v2.bump(Bump.PATCH, 2)
        self.assertEqual(v1, v2)
        v1.bump(Bump.PATCH)
        self.assertGreater(v1, v2)
        v2.bump(Bump.MINOR)
        self.assertGreater(v2, v1)
        v1.bump(Bump.MAJOR)
        self.assertGreater(v1, v2)

    def test_version_8(self):
        v1 = Version("2.0.1-batch")
        v2 = Version("2.0")
        self.assertGreater(v1, v2)
        self.assertLess(v2, v1)
        v2.bump(Bump.MINOR)
        self.assertGreater(v2, v1)
        v3 = Version(v1.bump(Bump.MINOR))
        self.assertEqual(v1, v3)
        self.assertLessEqual(v3, v2)

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
