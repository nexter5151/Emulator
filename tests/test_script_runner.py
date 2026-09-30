"""Тесты стартового скрипта."""

import tempfile
import unittest
from pathlib import Path

from src.config import EmulatorConfig
from src.script_runner import execute_script_line, read_script_lines


class TestScriptRunner(unittest.TestCase):
    def test_read_missing_file(self) -> None:
        lines, err = read_script_lines(Path("/nonexistent/script.script"))
        self.assertIsNone(lines)
        self.assertIsNotNone(err)
        assert err is not None
        self.assertIn("no such file", err)

    def test_skip_empty_line_logic(self) -> None:
        cfg = EmulatorConfig(vfs_path=None, startup_script=None)
        out, exit_flag, err = execute_script_line("   ", config=cfg)
        self.assertEqual(out, "")
        self.assertFalse(exit_flag)
        self.assertIsNone(err)

    def test_command_error_reported(self) -> None:
        cfg = EmulatorConfig(vfs_path=None, startup_script=None)
        out, exit_flag, err = execute_script_line("nope", config=cfg)
        self.assertIn("command not found", out)
        self.assertFalse(exit_flag)
        self.assertEqual(err, out)

    def test_read_utf8_script(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("ls\nconf-dump\n")
            path = Path(f.name)
        try:
            lines, err = read_script_lines(path)
            self.assertIsNone(err)
            assert lines is not None
            self.assertEqual(lines, ["ls", "conf-dump"])
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
