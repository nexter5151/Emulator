"""Состояние эмулятора: конфигурация и загруженная VFS."""

from __future__ import annotations

from dataclasses import dataclass

from src.config import EmulatorConfig
from src.vfs import (
    VirtualFileSystem,
    VfsNode,
    load_vfs,
    normalize_path,
    resolve_path,
)


@dataclass
class EmulatorRuntime:
    """Конфигурация запуска и данные VFS в памяти."""

    config: EmulatorConfig
    vfs: VirtualFileSystem | None = None
    vfs_load_error: str | None = None
    cwd: str = "/"

    @classmethod
    def from_config(cls, config: EmulatorConfig) -> EmulatorRuntime:
        """Создать runtime и загрузить VFS по пути из config."""
        vfs, err = load_vfs(config.vfs_path)
        return cls(config=config, vfs=vfs, vfs_load_error=err)

    @property
    def vfs_name(self) -> str:
        """Имя VFS для заголовка окна и приглашения."""
        if self.vfs is not None:
            return self.vfs.name
        return self.config.vfs_name

    def absolute_path(self, path: str) -> str:
        """Абсолютный путь относительно текущего каталога."""
        return normalize_path(self.cwd, path)

    def lookup(self, path: str) -> VfsNode | None:
        """Найти узел по относительному или абсолютному пути."""
        if self.vfs is None:
            return None
        return resolve_path(self.vfs, self.absolute_path(path))

    def conf_key_values(self) -> list[tuple[str, str]]:
        """Параметры для conf-dump с учётом состояния VFS."""
        rows = list(self.config.as_key_values())
        rows.append(("cwd", self.cwd))
        if self.config.vfs_path is None:
            rows.append(("vfs_loaded", "no"))
        elif self.vfs_load_error is not None:
            rows.append(("vfs_loaded", "error"))
            rows.append(("vfs_load_error", self.vfs_load_error))
        else:
            rows.append(("vfs_loaded", "yes"))
        return rows

    def format_conf_dump(self) -> str:
        """Форматированный conf-dump."""
        return "\n".join(
            f"{key}={value}" for key, value in self.conf_key_values()
        )
