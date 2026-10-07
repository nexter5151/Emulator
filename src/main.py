"""Точка входа эмулятора командной строки."""

from src.config import parse_args
from src.gui import ShellApp
from src.runtime import EmulatorRuntime


def main() -> None:
    config = parse_args()
    runtime = EmulatorRuntime.from_config(config)
    app = ShellApp(runtime)
    app.run()


if __name__ == "__main__":
    main()
