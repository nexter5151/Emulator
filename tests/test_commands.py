"""Тесты команд этапа 4: ls, cd, cat, rev, du."""

import unittest
from pathlib import Path

from src.commands import run_command
from src.config import EmulatorConfig
from src.runtime import EmulatorRuntime
from src.vfs import normalize_path


ROOT = Path(__file__).resolve().parent.parent
UNIX = ROOT / "examples" / "vfs" / "unix.xml"


def _runtime() -> EmulatorRuntime:
    cfg = EmulatorConfig(vfs_path=UNIX, startup_script=None)
    return EmulatorRuntime.from_config(cfg)


class TestNormalizePath(unittest.TestCase):
    def test_relative_nested(self) -> None:
        self.assertEqual(
            normalize_path("/", "home/user/data"),
            "/home/user/data",
        )

    def test_dotdot(self) -> None:
        self.assertEqual(
            normalize_path("/home/user/data", "../.."),
            "/home",
        )

    def test_mixed(self) -> None:
        self.assertEqual(
            normalize_path("/home", "user/data/../data/./notes.txt"),
            "/home/user/data/notes.txt",
        )


class TestCd(unittest.TestCase):
    def test_nested_relative(self) -> None:
        rt = _runtime()
        out, _ = run_command("cd", ["home/user/data"], rt)
        self.assertEqual(out, "")
        self.assertEqual(rt.cwd, "/home/user/data")

    def test_not_directory(self) -> None:
        rt = _runtime()
        out, _ = run_command("cd", ["readme.txt"], rt)
        self.assertIn("Not a directory", out)

    def test_missing(self) -> None:
        rt = _runtime()
        out, _ = run_command("cd", ["no/such"], rt)
        self.assertIn("No such file", out)


class TestLs(unittest.TestCase):
    def test_plain(self) -> None:
        rt = _runtime()
        out, _ = run_command("ls", [], rt)
        self.assertIn("home", out)
        self.assertIn("readme.txt", out)
        self.assertNotIn(".bashrc", out)

    def test_all(self) -> None:
        rt = _runtime()
        run_command("cd", ["home/user"], rt)
        out, _ = run_command("ls", ["-a"], rt)
        self.assertIn(".bashrc", out)
        self.assertIn(".", out)
        self.assertIn("..", out)

    def test_long_human(self) -> None:
        rt = _runtime()
        out, _ = run_command("ls", ["-lh", "readme.txt"], rt)
        self.assertIn("readme.txt", out)
        self.assertIn("-rw-r--r--", out)

    def test_la_combo(self) -> None:
        rt = _runtime()
        run_command("cd", ["home/user"], rt)
        out, _ = run_command("ls", ["-la"], rt)
        self.assertIn(".bashrc", out)
        self.assertIn("drwxr-xr-x", out)


class TestCatRevDu(unittest.TestCase):
    def test_cat(self) -> None:
        rt = _runtime()
        out, _ = run_command(
            "cat",
            ["home/user/data/notes.txt"],
            rt,
        )
        self.assertIn("hello world", out)

    def test_rev(self) -> None:
        rt = _runtime()
        out, _ = run_command(
            "rev",
            ["home/user/data/notes.txt"],
            rt,
        )
        self.assertIn("dlrow olleh", out)

    def test_du(self) -> None:
        rt = _runtime()
        out, _ = run_command("du", ["home/user/data"], rt)
        size_part = out.split("\t")[0]
        self.assertTrue(size_part.isdigit())
        self.assertGreater(int(size_part), 0)


if __name__ == "__main__":
    unittest.main()
