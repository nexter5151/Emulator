"""Обработка команд эмулятора командной строки."""


def run_command(command: str, args: list[str]) -> tuple[str, bool]:
    """Выполнить команду эмулятора с переданными аргументами.

    Команды ls и cd работают в режиме заглушек и выводят имя команды
    вместе с переданными аргументами. Команда exit сигнализирует
    о завершении работы программы.

    Args:
        command: Название вызываемой команды.
        args: Список строковых аргументов команды.

    Returns:
        Кортеж из двух элементов:
            - str: сообщение о результате выполнения команды или ошибка;
            - bool: флаг завершения работы (True для команды exit,
              иначе False).
    """
    if command == "ls":
        if args:
            return "ls: " + " ".join(args), False
        return "ls", False

    if command == "cd":
        if args:
            return "cd: " + " ".join(args), False
        return "cd", False

    if command == "exit":
        return "", True

    return command + ": command not found", False
