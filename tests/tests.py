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

from src.deploy.program import Program
from src.deploy.version import Version, Bump


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.git = Program("git", "Git")
        self.zip = Program("7z", "7-Zip")
        self.gh = Program("gh", "GihHub CLI")

    def tearDown(self):
        pass

    def test_programs_can_be_run(self):
        programs = [(self.git, ["-v"]), (self.zip, None), (self.gh, None)]
        [self.assertTrue(a.exists()) for a, _ in programs]
        [self.assertTrue(a.runnable(params=b)) for a, b in programs]

    def test_program_runnable_raise(self):
        self.assertTrue(self.git.exists())
        self.assertFalse(self.git.runnable())
        with self.assertRaises(RuntimeError):
            self.git.runnable(True)

    def test_program_exists_raise(self):
        p = Program("@")
        self.assertFalse(p.exists())
        with self.assertRaises(RuntimeError):
            p.exists(True)

    def test_program_output(self):
        result = []
        self.zip.execute(["-h"], stdout_cb=None, stderr_cb=lambda x: result.append(x))
        self.assertListEqual(result, [])
        self.zip.execute(["-h"], stdout_cb=lambda x: result.append(x))
        self.assertGreater(len(result), 0)

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


if __name__ == '__main__':
    unittest.main()
