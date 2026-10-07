"""Выполнение стартового скрипта команд эмулятора."""

from __future__ import annotations

from pathlib import Path

from src.commands import run_command
from src.parser import parse_input
from src.runtime import EmulatorRuntime


def read_script_lines(path: Path) -> tuple[list[str] | None, str | None]:
    """Прочитать строки скрипта.

    Returns:
        (lines, error_message) — при ошибке lines is None.
    """
    if not path.is_file():
        return None, f"startup script: {path}: no such file"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"startup script: {path}: {exc}"
    return text.splitlines(), None


def execute_script_line(
    line: str,
    *,
    runtime: EmulatorRuntime,
) -> tuple[str, bool, str | None]:
    """Выполнить одну строку скрипта.

    Returns:
        (output_text, should_exit, error_message)
        error_message set when command failed but execution continues.
    """
    command, args = parse_input(line)
    if command is None:
        return "", False, None

    text, should_exit = run_command(command, args, runtime)
    error: str | None = None
    if text and "command not found" in text:
        error = text
    return text, should_exit, error
