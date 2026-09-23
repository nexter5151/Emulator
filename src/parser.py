"""Парсер ввода командной строки эмулятора."""


def parse_input(line: str) -> tuple[str | None, list[str]]:
    """Разбить введенную строку на название команды и список аргументов.

    Args:
        line: Сырая строка ввода из командной строки.

    Returns:
        Кортеж из двух элементов:
            - str или None: название команды либо None, если строка пуста;
            - list[str]: список переданных аргументов команды.
    """
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]
