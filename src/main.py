"""Точка входа эмулятора командной строки."""

from src.config import parse_args
from src.gui import ShellApp


def main() -> None:
    config = parse_args()
    app = ShellApp(config)
    app.run()


if __name__ == "__main__":
    main()
