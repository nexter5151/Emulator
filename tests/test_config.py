"""Тесты конфигурации и conf-dump."""

import unittest
from pathlib import Path

from src.commands import run_command
from src.config import EmulatorConfig, format_startup_debug, parse_args


class TestParseArgs(unittest.TestCase):
    def test_defaults(self) -> None:
        cfg = parse_args([])
        self.assertIsNone(cfg.vfs_path)
        self.assertIsNone(cfg.startup_script)
        self.assertEqual(cfg.vfs_name, "stub-vfs")

    def test_vfs_and_script(self) -> None:
        cfg = parse_args([
            "--vfs", "/tmp/myvfs",
            "--script", "/tmp/init.script",
        ])
        self.assertEqual(cfg.vfs_path, Path("/tmp/myvfs"))
        self.assertEqual(cfg.startup_script, Path("/tmp/init.script"))
        self.assertEqual(cfg.vfs_name, "myvfs")


class TestConfDump(unittest.TestCase):
    def test_format_dump(self) -> None:
        cfg = EmulatorConfig(
            vfs_path=Path("/data/vfs1"),
            startup_script=Path("/data/run.script"),
        )
        text = cfg.format_dump()
        self.assertIn("vfs_path=/data/vfs1", text)
        self.assertIn("startup_script=/data/run.script", text)
        self.assertIn("vfs_name=vfs1", text)

    def test_conf_dump_command(self) -> None:
        cfg = EmulatorConfig(vfs_path=None, startup_script=None)
        out, exit_flag = run_command("conf-dump", [], cfg)
        self.assertFalse(exit_flag)
        self.assertIn("vfs_name=stub-vfs", out)


class TestStartupDebug(unittest.TestCase):
    def test_contains_all_keys(self) -> None:
        cfg = EmulatorConfig(vfs_path=Path("/a"), startup_script=None)
        block = format_startup_debug(cfg)
        self.assertIn("[config] vfs_path=/a", block)
        self.assertIn("[config] startup_script=", block)


if __name__ == "__main__":
    unittest.main()
