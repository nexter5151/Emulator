"""Модуль графического интерфейса эмулятора командной строки UNIX.

Реализует окно терминала с областью вывода истории команд и строкой ввода.
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import scrolledtext

from src.commands import run_command
from src.config import format_startup_debug
from src.parser import parse_input
from src.runtime import EmulatorRuntime
from src.script_runner import execute_script_line, read_script_lines


class ShellApp:
    """Графическое приложение-эмулятор командной строки."""

    def __init__(self, runtime: EmulatorRuntime) -> None:
        """Инициализировать главное окно приложения и его компоненты."""
        self.runtime = runtime
        self.user_prompt = runtime.vfs_name + "$ "

        self.root = tk.Tk()
        self.root.title("Shell Emulator — " + runtime.vfs_name)
        self.root.geometry("600x400")

        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_label = tk.Label(input_frame, text=self.user_prompt)
        self.prompt_label.pack(side=tk.LEFT)

        self.input = tk.Entry(input_frame)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input.bind("<Return>", self.on_enter)
        self.input.focus()

        self.write("Shell Emulator (VFS: " + runtime.vfs_name + ")\n")
        self._emit_startup_debug()
        self._emit_vfs_load_status()
        self._run_startup_script()

    def _emit_startup_debug(self) -> None:
        """Отладочный вывод параметров при запуске (GUI и stderr)."""
        block = format_startup_debug(self.runtime.config) + "\n"
        print(block, file=sys.stderr, end="")
        self.write(block)

    def _emit_vfs_load_status(self) -> None:
        """Сообщить об ошибке загрузки VFS при старте."""
        err = self.runtime.vfs_load_error
        if err is None:
            return
        line = err + "\n"
        print(line, file=sys.stderr, end="")
        self.write(line)

    def _run_startup_script(self) -> None:
        """Выполнить стартовый скрипт, имитируя интерактивный диалог."""
        path = self.runtime.config.startup_script
        if path is None:
            return

        lines, load_error = read_script_lines(path)
        if load_error is not None:
            self.write(load_error + "\n")
            return

        assert lines is not None

        errors = 0
        for raw_line in lines:
            result = self._execute_dialog_line(raw_line)
            if result[1]:
                errors += 1
            if result[0]:
                return
        if errors > 0:
            self.write("script executed with errors" + "\n")


    def _execute_dialog_line(self, line: str) -> bool | tuple[bool, bool]:
        """Показать ввод/вывод одной строки.
        True — нужно завершить приложение.
        """
        stripped = line.strip()
        if not stripped:
            return False

        self.write(self.user_prompt + stripped + "\n")
        text, should_exit, error = execute_script_line(
            stripped, runtime=self.runtime
        )
        with_error = False
        if text:
            self.write(text + "\n")
        if error is not None:
            with_error = True
            self.write("script error: " + error + "\n")
        return should_exit, with_error

    def write(self, text: str) -> None:
        """Вывести текст в область терминала с автоматической прокруткой."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def on_enter(self, event: tk.Event) -> None:
        """Обработать событие нажатия клавиши Enter в строке ввода."""
        line = self.input.get()
        self.input.delete(0, tk.END)

        self.write(self.user_prompt + line + "\n")

        command, args = parse_input(line)
        if command is None:
            return

        text, should_exit = run_command(command, args, self.runtime)
        if text:
            self.write(text + "\n")
        if should_exit:
            self.root.destroy()

    def run(self) -> None:
        """Запустить главный цикл обработки событий GUI."""
        self.root.mainloop()
