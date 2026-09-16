import unittest

from src.commands import run_command


class TestCommands(unittest.TestCase):
    def test_ls(self):
        text, exit_flag = run_command("ls", [])
        self.assertEqual(text, "ls")
        self.assertFalse(exit_flag)

    def test_ls_args(self):
        text, exit_flag = run_command("ls", ["-l"])
        self.assertEqual(text, "ls: -l")
        self.assertFalse(exit_flag)

    def test_cd(self):
        text, exit_flag = run_command("cd", ["/tmp"])
        self.assertEqual(text, "cd: /tmp")

    def test_exit(self):
        text, exit_flag = run_command("exit", [])
        self.assertTrue(exit_flag)

    def test_unknown(self):
        text, exit_flag = run_command("foo", [])
        self.assertIn("command not found", text)


if __name__ == "__main__":
    unittest.main()
