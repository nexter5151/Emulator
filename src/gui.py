import tkinter as tk
from tkinter import scrolledtext

from src.commands import run_command
from src.parser import parse_input

VFS_NAME = "stub-vfs"


class ShellApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shell Emulator — " + VFS_NAME)
        self.root.geometry("600x400")

        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.input = tk.Entry(self.root)
        self.input.pack(fill=tk.X, padx=5, pady=5)
        self.input.bind("<Return>", self.on_enter)
        self.input.focus()

        self.write("Shell Emulator (VFS: " + VFS_NAME + ")\n")

    def write(self, text):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def on_enter(self, event):
        line = self.input.get()
        self.input.delete(0, tk.END)

        self.write("$ " + line + "\n")

        command, args = parse_input(line)
        if command is None:
            return

        text, should_exit = run_command(command, args)
        if text:
            self.write(text + "\n")
        if should_exit:
            self.root.destroy()

    def run(self):
        self.root.mainloop()
