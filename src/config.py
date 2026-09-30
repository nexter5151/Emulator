"""Конфигурация эмулятора: параметры командной строки и их представление."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EmulatorConfig:
    """Параметры запуска эмулятора."""

    vfs_path: Path | None
    startup_script: Path | None

    @property
    def vfs_name(self) -> str:
        """Имя VFS для заголовка окна и приглашения."""
        if self.vfs_path is None:
            return "stub-vfs"
        return self.vfs_path.name or str(self.vfs_path)

    def as_key_values(self) -> list[tuple[str, str]]:
        """Все параметры в виде пар ключ–значение для отладки и conf-dump."""
        return [
            ("vfs_path", _path_display(self.vfs_path)),
            ("startup_script", _path_display(self.startup_script)),
            ("vfs_name", self.vfs_name),
        ]

    def format_dump(self) -> str:
        """Форматированный вывод параметров
        (ключ=значение, по одному на строку).
        """
        return "\n".join(
            f"{key}={value}" for key, value in self.as_key_values()
        )


def _path_display(path: Path | None) -> str:
    if path is None:
        return ""
    return str(path)


def parse_args(argv: list[str] | None = None) -> EmulatorConfig:
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        type=Path,
        default=None,
        help="Путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        dest="startup_script",
        type=Path,
        default=None,
        help="Путь к стартовому скрипту команд эмулятора",
    )
    ns = parser.parse_args(argv)
    return EmulatorConfig(
        vfs_path=ns.vfs_path,
        startup_script=ns.startup_script,
    )


def format_startup_debug(config: EmulatorConfig) -> str:
    """Отладочный блок параметров при запуске."""
    lines = ["[config] emulator parameters:"]
    for key, value in config.as_key_values():
        lines.append(f"[config] {key}={value}")
    return "\n".join(lines)
