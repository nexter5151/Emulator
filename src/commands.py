"""Обработка команд эмулятора командной строки."""

from __future__ import annotations

from src.runtime import EmulatorRuntime
from src.vfs import format_tree


def run_command(
    command: str,
    args: list[str],
    runtime: EmulatorRuntime,
) -> tuple[str, bool]:
    """Выполнить команду эмулятора с переданными аргументами.

    Args:
        command: Название вызываемой команды.
        args: Список строковых аргументов команды.
        runtime: Конфигурация и состояние VFS.

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
        return runtime.format_conf_dump(), False

    if command == "vfs-tree":
        return _cmd_vfs_tree(args, runtime), False

    if command == "exit":
        return "", True

    return command + ": command not found", False


def _cmd_vfs_tree(args: list[str], runtime: EmulatorRuntime) -> str:
    if runtime.vfs is None:
        if runtime.vfs_load_error is not None:
            return runtime.vfs_load_error
        return "vfs-tree: VFS is not loaded"
    path = args[0] if args else "/"
    return format_tree(runtime.vfs, path)
