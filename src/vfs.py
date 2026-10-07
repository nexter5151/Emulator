"""Виртуальная файловая система в памяти и загрузка из XML."""

from __future__ import annotations

import base64
import binascii
import xml.etree.ElementTree as element_tree
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

_SIZE_UNIT_BASE = 1024


@dataclass
class VfsFile:
    """Файл VFS с содержимым в памяти."""

    name: str
    content: bytes


@dataclass
class VfsDirectory:
    """Каталог VFS с дочерними элементами."""

    name: str
    children: dict[str, VfsNode] = field(default_factory=dict)


VfsNode = Union[VfsFile, VfsDirectory]


@dataclass
class VirtualFileSystem:
    """Загруженная VFS целиком."""

    name: str
    root: VfsDirectory


def load_vfs(
    path: Path | None,
) -> tuple[VirtualFileSystem | None, str | None]:
    """Загрузить VFS из XML-файла.

    Returns:
        (vfs, error) — при ошибке vfs is None.
    """
    if path is None:
        return None, None
    if not path.is_file():
        return None, f"vfs: {path}: no such file"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"vfs: {path}: {exc}"
    try:
        element = element_tree.fromstring(raw)
    except element_tree.ParseError:
        return None, f"vfs: {path}: invalid XML format"
    try:
        return _parse_vfs_element(element, path), None
    except ValueError as exc:
        return None, f"vfs: {path}: invalid format: {exc}"


def _parse_vfs_element(
    element: element_tree.Element,
    path: Path,
) -> VirtualFileSystem:
    if element.tag != "vfs":
        raise ValueError("root element must be <vfs>")
    name = element.get("name") or path.stem or "vfs"
    root = VfsDirectory(name="/")
    for child in element:
        node = _parse_node(child)
        _add_child(root, node)
    return VirtualFileSystem(name=name, root=root)


def _parse_node(element: element_tree.Element) -> VfsNode:
    if element.tag == "directory":
        return _parse_directory(element)
    if element.tag == "file":
        return _parse_file(element)
    raise ValueError(f"unknown element <{element.tag}>")


def _parse_directory(element: element_tree.Element) -> VfsDirectory:
    dir_name = element.get("name")
    if not dir_name:
        raise ValueError("directory without name")
    directory = VfsDirectory(name=dir_name)
    for child in element:
        node = _parse_node(child)
        _add_child(directory, node)
    return directory


def _parse_file(element: element_tree.Element) -> VfsFile:
    file_name = element.get("name")
    if not file_name:
        raise ValueError("file without name")
    encoding = element.get("encoding", "text")
    text = element.text or ""
    if encoding == "text":
        content = text.encode("utf-8")
    elif encoding == "base64":
        try:
            content = base64.b64decode(text.strip(), validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError(f"bad base64 in {file_name}") from exc
    else:
        raise ValueError(f"unknown encoding {encoding!r}")
    return VfsFile(name=file_name, content=content)


def _add_child(parent: VfsDirectory, node: VfsNode) -> None:
    if node.name in parent.children:
        raise ValueError(f"duplicate name {node.name!r}")
    parent.children[node.name] = node


def normalize_path(cwd: str, path: str) -> str:
    """Собрать абсолютный путь из cwd и path (., .., относительные)."""
    if path.startswith("/"):
        parts: list[str] = []
    else:
        parts = [p for p in cwd.split("/") if p]
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/" + "/".join(parts) if parts else "/"


def resolve_path(vfs: VirtualFileSystem, path: str) -> VfsNode | None:
    """Найти узел по абсолютному пути (/a/b)."""
    cleaned = path.strip() or "/"
    if not cleaned.startswith("/"):
        return None
    parts = [p for p in cleaned.split("/") if p]
    current: VfsNode = vfs.root
    for part in parts:
        if not isinstance(current, VfsDirectory):
            return None
        child = current.children.get(part)
        if child is None:
            return None
        current = child
    return current


def create_directory(
    vfs: VirtualFileSystem,
    abs_path: str,
    parents: bool,
) -> str | None:
    """Создать каталог в памяти. None — успех, иначе текст ошибки."""
    if abs_path == "/":
        if parents:
            return None
        return "File exists"
    parts = [p for p in abs_path.split("/") if p]
    current = vfs.root
    last_index = len(parts) - 1
    for index, part in enumerate(parts):
        is_last = index == last_index
        error = _mkdir_step(current, part, is_last, parents)
        if error is not None:
            return error
        child = current.children[part]
        assert isinstance(child, VfsDirectory)
        current = child
    return None


def _mkdir_step(
    current: VfsDirectory,
    part: str,
    is_last: bool,
    parents: bool,
) -> str | None:
    """Один шаг создания пути для mkdir."""
    child = current.children.get(part)
    if child is None:
        if not parents and not is_last:
            return "No such file or directory"
        current.children[part] = VfsDirectory(name=part)
        return None
    if isinstance(child, VfsFile):
        return "File exists"
    if is_last and not parents:
        return "File exists"
    return None


def node_size(node: VfsNode) -> int:
    """Размер файла или суммарный размер каталога (рекурсивно)."""
    if isinstance(node, VfsFile):
        return len(node.content)
    total = 0
    for child in node.children.values():
        total += node_size(child)
    return total


def human_size(size: int) -> str:
    """Человекочитаемый размер (как ls -h / du -h)."""
    units = ("B", "K", "M", "G", "T")
    value = float(size)
    for unit in units:
        if value < _SIZE_UNIT_BASE or unit == units[-1]:
            if unit == "B":
                return f"{int(value)}{unit}"
            text = f"{value:.1f}".rstrip("0").rstrip(".")
            return f"{text}{unit}"
        value /= _SIZE_UNIT_BASE
    return f"{size}B"


def format_tree(vfs: VirtualFileSystem, start: str = "/") -> str:
    """Текстовое дерево каталогов от заданного пути."""
    node = resolve_path(vfs, start)
    if node is None:
        return f"vfs-tree: {start}: no such file or directory"
    if isinstance(node, VfsFile):
        return start.rstrip("/") + "  [file]"
    lines: list[str] = [start.rstrip("/") or "/"]
    _append_tree(node, start.rstrip("/") or "", lines)
    return "\n".join(lines)


def _append_tree(
    directory: VfsDirectory,
    prefix: str,
    lines: list[str],
) -> None:
    names = sorted(directory.children.keys())
    for name in names:
        child = directory.children[name]
        if isinstance(child, VfsDirectory):
            path = f"{prefix}/{name}" if prefix else f"/{name}"
            lines.append(path)
            _append_tree(child, path, lines)
        else:
            mark = f"{prefix}/{name}" if prefix else f"/{name}"
            lines.append(f"{mark}  [file]")
