"""Обработка команд эмулятора командной строки."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import EmulatorConfig


def run_command(
    command: str,
    args: list[str],
    config: EmulatorConfig,
) -> tuple[str, bool]:
    """Выполнить команду эмулятора с переданными аргументами.

    Args:
        command: Название вызываемой команды.
        args: Список строковых аргументов команды.
        config: Текущая конфигурация эмулятора.

    Returns:
        Кортеж из двух элементов:
            - str: сообщение о результате выполнения команды или ошибка;
            - bool: флаг завершения работы (True для команды exit).
    """
    if command == "ls":
        if args:
            return "ls: " + " ".join(args), False
        return "ls", False

    if command == "cd":
        if args:
            return "cd: " + " ".join(args), False
        return "cd", False

    if command == "conf-dump":
        return config.format_dump(), False

    if command == "exit":
        return "", True

    return command + ": command not found", False
