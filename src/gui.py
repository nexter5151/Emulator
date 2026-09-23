"""Модуль графического интерфейса эмулятора командной строки UNIX.

Реализует окно терминала с областью вывода истории команд и строкой ввода.
"""

import tkinter as tk
from tkinter import scrolledtext

from src.commands import run_command
from src.parser import parse_input

VFS_NAME = "stub-vfs"
USER_PROMPT = VFS_NAME + "$ "


class ShellApp:
    """Графическое приложение-эмулятор командной строки."""

    def __init__(self) -> None:
        """Инициализировать главное окно приложения и его компоненты."""
        self.root = tk.Tk()
        self.root.title("Shell Emulator — " + VFS_NAME)
        self.root.geometry("600x400")

        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_label = tk.Label(input_frame, text=USER_PROMPT)
        self.prompt_label.pack(side=tk.LEFT)

        self.input = tk.Entry(input_frame)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input.bind("<Return>", self.on_enter)
        self.input.focus()

        self.write("Shell Emulator (VFS: " + VFS_NAME + ")\n")

    def write(self, text: str) -> None:
        """Вывести текст в область терминала с автоматической прокруткой.

        Args:
            text: Строка для отображения в окне вывода.
        """
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def on_enter(self, event: tk.Event) -> None:
        """Обработать событие нажатия клавиши Enter в строке ввода.

        Считывает строку, передает ее в парсер и обработчик команд,
        после чего выводит результат или закрывает окно при выходе.

        Args:
            event: Событие клавиатуры Tkinter.
        """
        line = self.input.get()
        self.input.delete(0, tk.END)

        self.write(USER_PROMPT + line + "\n")

        command, args = parse_input(line)
        if command is None:
            return

        text, should_exit = run_command(command, args)
        if text:
            self.write(text + "\n")
        if should_exit:
            self.root.destroy()

    def run(self) -> None:
        """Запустить главный цикл обработки событий GUI."""
        self.root.mainloop()