"""Обработка команд эмулятора командной строки."""

from __future__ import annotations

from src.runtime import EmulatorRuntime
from src.vfs import (
    VfsDirectory,
    VfsFile,
    VfsNode,
    format_tree,
    human_size,
    node_size,
)


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
    handlers = {
        "ls": _cmd_ls,
        "cd": _cmd_cd,
        "cat": _cmd_cat,
        "rev": _cmd_rev,
        "du": _cmd_du,
        "conf-dump": lambda a, r: r.format_conf_dump(),
        "vfs-tree": _cmd_vfs_tree,
    }
    if command == "exit":
        return "", True
    handler = handlers.get(command)
    if handler is None:
        return command + ": command not found", False
    return handler(args, runtime), False


def _require_vfs(runtime: EmulatorRuntime, cmd: str) -> str | None:
    if runtime.vfs is None:
        if runtime.vfs_load_error is not None:
            return runtime.vfs_load_error
        return f"{cmd}: VFS is not loaded"
    return None


def _cmd_vfs_tree(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "vfs-tree")
    if err is not None:
        return err
    assert runtime.vfs is not None
    raw = args[0] if args else "."
    path = runtime.absolute_path(raw)
    return format_tree(runtime.vfs, path)


def _parse_ls_flags(
    args: list[str],
) -> tuple[bool, bool, bool, list[str], str | None]:
    show_all = False
    long_fmt = False
    human = False
    paths: list[str] = []
    for arg in args:
        if arg.startswith("-") and len(arg) > 1:
            for ch in arg[1:]:
                if ch == "a":
                    show_all = True
                elif ch == "l":
                    long_fmt = True
                elif ch == "h":
                    human = True
                else:
                    return (
                        False,
                        False,
                        False,
                        [],
                        f"ls: invalid option -- '{ch}'",
                    )
        else:
            paths.append(arg)
    return show_all, long_fmt, human, paths, None


def _cmd_ls(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "ls")
    if err is not None:
        return err
    show_all, long_fmt, human, paths, opt_err = _parse_ls_flags(args)
    if opt_err is not None:
        return opt_err
    if not paths:
        paths = ["."]
    blocks: list[str] = []
    for target in paths:
        block = _ls_one(runtime, target, show_all, long_fmt, human)
        blocks.append(block)
    if len(paths) == 1:
        return blocks[0]
    named: list[str] = []
    for target, block in zip(paths, blocks):
        named.append(f"{target}:\n{block}" if block else f"{target}:")
    return "\n\n".join(named)


def _ls_one(
    runtime: EmulatorRuntime,
    target: str,
    show_all: bool,
    long_fmt: bool,
    human: bool,
) -> str:
    node = runtime.lookup(target)
    if node is None:
        return f"ls: {target}: No such file or directory"
    if isinstance(node, VfsFile):
        return _ls_entry(node.name, node, long_fmt, human)
    assert isinstance(node, VfsDirectory)
    names = _ls_names(node, show_all)
    lines = [
        _ls_entry(name, _ls_child(node, name), long_fmt, human)
        for name in names
    ]
    return "\n".join(lines)


def _ls_names(directory: VfsDirectory, show_all: bool) -> list[str]:
    names = sorted(directory.children.keys())
    if not show_all:
        names = [n for n in names if not n.startswith(".")]
    else:
        names = [".", ".."] + names
    return names


def _ls_child(directory: VfsDirectory, name: str) -> VfsNode | None:
    if name in (".", ".."):
        return directory
    return directory.children.get(name)


def _ls_entry(
    name: str,
    node: VfsNode | None,
    long_fmt: bool,
    human: bool,
) -> str:
    if not long_fmt:
        return name
    if node is None:
        return f"?????????? {name}"
    is_dir = isinstance(node, VfsDirectory)
    mode = "drwxr-xr-x" if is_dir else "-rw-r--r--"
    size = node_size(node)
    size_text = human_size(size) if human else str(size)
    return f"{mode} {size_text:>8} {name}"


def _cmd_cd(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "cd")
    if err is not None:
        return err
    if len(args) > 1:
        return "cd: too many arguments"
    target = args[0] if args else "/"
    abs_path = runtime.absolute_path(target)
    node = runtime.lookup(target)
    if node is None:
        return f"cd: {target}: No such file or directory"
    if not isinstance(node, VfsDirectory):
        return f"cd: {target}: Not a directory"
    runtime.cwd = abs_path
    return ""


def _cmd_cat(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "cat")
    if err is not None:
        return err
    if not args:
        return "cat: missing file operand"
    parts: list[str] = []
    for path in args:
        parts.append(_read_file_text(runtime, path, "cat"))
    return "\n".join(parts)


def _cmd_rev(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "rev")
    if err is not None:
        return err
    if not args:
        return "rev: missing file operand"
    parts: list[str] = []
    for path in args:
        text = _read_file_text(runtime, path, "rev")
        if text.startswith("rev:"):
            parts.append(text)
            continue
        lines = text.splitlines()
        parts.append("\n".join(line[::-1] for line in lines))
    return "\n".join(parts)


def _read_file_text(
    runtime: EmulatorRuntime,
    path: str,
    cmd: str,
) -> str:
    node = runtime.lookup(path)
    if node is None:
        return f"{cmd}: {path}: No such file or directory"
    if isinstance(node, VfsDirectory):
        return f"{cmd}: {path}: Is a directory"
    assert isinstance(node, VfsFile)
    return node.content.decode("utf-8", errors="replace")


def _cmd_du(args: list[str], runtime: EmulatorRuntime) -> str:
    err = _require_vfs(runtime, "du")
    if err is not None:
        return err
    human = False
    paths: list[str] = []
    for arg in args:
        if arg in ("-h", "--human-readable"):
            human = True
        elif arg.startswith("-") and arg != "-":
            return f"du: invalid option -- '{arg[1:]}'"
        else:
            paths.append(arg)
    if not paths:
        paths = ["."]
    lines: list[str] = []
    for path in paths:
        lines.append(_du_one(runtime, path, human))
    return "\n".join(lines)


def _du_one(
    runtime: EmulatorRuntime,
    path: str,
    human: bool,
) -> str:
    node = runtime.lookup(path)
    if node is None:
        return f"du: {path}: No such file or directory"
    size = node_size(node)
    size_text = human_size(size) if human else str(size)
    shown = runtime.absolute_path(path)
    return f"{size_text}\t{shown}"
