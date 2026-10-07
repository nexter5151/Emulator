"""Тесты загрузки VFS и команды vfs-tree."""

import unittest
from pathlib import Path

from src.commands import run_command
from src.config import EmulatorConfig
from src.runtime import EmulatorRuntime
from src.vfs import load_vfs, resolve_path, VfsFile


ROOT = Path(__file__).resolve().parent.parent
VFS_DIR = ROOT / "examples" / "vfs"


class TestLoadVfs(unittest.TestCase):
    def test_minimal(self) -> None:
        vfs, err = load_vfs(VFS_DIR / "minimal.xml")
        self.assertIsNone(err)
        assert vfs is not None
        self.assertEqual(vfs.name, "minimal")
        only = vfs.root.children["only.txt"]
        self.assertIsInstance(only, VfsFile)
        assert isinstance(only, VfsFile)
        self.assertEqual(only.content, b"single file at root")

    def test_deep_three_levels(self) -> None:
        vfs, err = load_vfs(VFS_DIR / "deep.xml")
        self.assertIsNone(err)
        assert vfs is not None
        node = resolve_path(vfs, "/level1/level2/level3/leaf.txt")
        self.assertIsInstance(node, VfsFile)

    def test_missing_file(self) -> None:
        vfs, err = load_vfs(VFS_DIR / "missing.xml")
        self.assertIsNone(vfs)
        assert err is not None
        self.assertIn("no such file", err)

    def test_invalid_xml(self) -> None:
        vfs, err = load_vfs(VFS_DIR / "invalid.xml")
        self.assertIsNone(vfs)
        assert err is not None
        self.assertIn("invalid XML", err)

    def test_duplicate_names(self) -> None:
        vfs, err = load_vfs(VFS_DIR / "broken.xml")
        self.assertIsNone(vfs)
        assert err is not None
        self.assertIn("duplicate", err)


class TestVfsTreeCommand(unittest.TestCase):
    def test_tree_from_deep_vfs(self) -> None:
        cfg = EmulatorConfig(
            vfs_path=VFS_DIR / "deep.xml",
            startup_script=None,
        )
        runtime = EmulatorRuntime.from_config(cfg)
        out, exit_flag = run_command("vfs-tree", [], runtime)
        self.assertFalse(exit_flag)
        self.assertIn("/level1/level2/level3", out)
        self.assertIn("[file]", out)

    def test_tree_without_vfs(self) -> None:
        cfg = EmulatorConfig(vfs_path=None, startup_script=None)
        runtime = EmulatorRuntime.from_config(cfg)
        out, _ = run_command("vfs-tree", [], runtime)
        self.assertIn("not loaded", out)


class TestRuntimeVfsName(unittest.TestCase):
    def test_name_from_xml(self) -> None:
        cfg = EmulatorConfig(
            vfs_path=VFS_DIR / "multi.xml",
            startup_script=None,
        )
        runtime = EmulatorRuntime.from_config(cfg)
        self.assertEqual(runtime.vfs_name, "multi")

    def test_conf_dump_loaded(self) -> None:
        cfg = EmulatorConfig(
            vfs_path=VFS_DIR / "minimal.xml",
            startup_script=None,
        )
        runtime = EmulatorRuntime.from_config(cfg)
        out, _ = run_command("conf-dump", [], runtime)
        self.assertIn("vfs_loaded=yes", out)


if __name__ == "__main__":
    unittest.main()
