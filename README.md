# Shell Emulator

## 1. Общее описание

Эмулятор командной оболочки UNIX-подобной ОС (вариант №4).
Реализованы этапы 1–3: REPL в GUI, параметры командной строки,
стартовый скрипт, служебные команды `conf-dump` и `vfs-tree`,
загрузка виртуальной файловой системы (VFS) из XML в память.

Язык реализации: Python 3.
Интерфейс: tkinter (стандартная библиотека).

## 2. Функции и настройки

### Модули

| Файл | Назначение |
|------|------------|
| `src/main.py` | Точка входа, создание runtime и запуск GUI |
| `src/gui.py` | Графический интерфейс (окно, ввод, вывод) |
| `src/parser.py` | Парсер: разбивает строку на команду и аргументы |
| `src/commands.py` | Команды `ls`, `cd`, `conf-dump`, `vfs-tree`, `exit` |
| `src/config.py` | Параметры командной строки и отладочный вывод |
| `src/runtime.py` | Состояние эмулятора: config + загруженная VFS |
| `src/vfs.py` | Модель VFS в памяти и разбор XML |
| `src/script_runner.py` | Чтение и выполнение стартового скрипта |

### Формат XML VFS

Корневой элемент — `<vfs name="имя">`. Внутри — вложенные
`<directory name="...">` и `<file name="..." encoding="text|base64">`.
Текст файла — тело элемента; для двоичных данных — base64.
Данные только в памяти, исходный файл на диске не изменяется.

Примеры: `examples/vfs/minimal.xml`, `multi.xml`, `deep.xml`.

### Описание функций (этап 3)

#### `src/vfs.py`

| Имя | Назначение |
|-----|------------|
| `load_vfs(path)` | Загрузка XML; ошибки «no such file», «invalid XML format», «invalid format». |
| `resolve_path(vfs, path)` | Поиск узла по абсолютному пути. |
| `format_tree(vfs, start="/")` | Дерево каталогов для команды `vfs-tree`. |

#### `src/runtime.py`

| Имя | Назначение |
|-----|------------|
| `EmulatorRuntime` | Config, объект VFS и текст ошибки загрузки. |
| `EmulatorRuntime.from_config(config)` | Загрузка VFS по `config.vfs_path`. |
| `EmulatorRuntime.vfs_name` | Имя из XML (`name`) или из пути / `stub-vfs`. |
| `format_conf_dump()` | `conf-dump` с полями `vfs_loaded`, `vfs_load_error`. |

#### `src/commands.py` (этап 3)

| Имя | Назначение |
|-----|------------|
| `run_command(..., runtime)` | Принимает `EmulatorRuntime` вместо `EmulatorConfig`. |
| `vfs-tree [path]` | Дерево VFS; без `--vfs` — сообщение, что VFS не загружена. |

#### `src/gui.py` (этап 3)

| Имя | Назначение |
|-----|------------|
| `ShellApp(runtime)` | Заголовок и приглашение из `runtime.vfs_name`. |
| `_emit_vfs_load_status()` | Вывод ошибки загрузки VFS при старте. |

### Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `--vfs PATH` | Путь к XML-файлу VFS |
| `--script PATH` | Путь к стартовому скрипту (команды по одной на строку) |

При запуске в окне и в stderr выводится блок `[config]` со всеми
параметрами. Без `--vfs` имя VFS по умолчанию — `stub-vfs`.

### Команды эмулятора

| Команда | Описание |
|---------|----------|
| `ls [аргументы]` | Заглушка: выводит имя команды и аргументы |
| `cd [аргументы]` | Заглушка: выводит имя команды и аргументы |
| `conf-dump` | Параметры эмулятора и статус VFS |
| `vfs-tree [path]` | Дерево каталогов загруженной VFS (этап 3) |
| `exit` | Завершение работы приложения |

Неизвестная команда выводит сообщение об ошибке:
`<команда>: command not found`.

## 3. Сборка и запуск

Сборка не требуется — проект использует только стандартную
библиотеку Python.

### Запуск приложения

```bash
./run.sh
```

```bash
python3 -m src.main --vfs examples/vfs/deep.xml --script examples/startup_stage3.script
```

### Скрипты проверки (этапы 2–3)

```bash
chmod +x scripts/*.sh
./scripts/test_no_args.sh
./scripts/test_vfs_only.sh
./scripts/test_script_only.sh
./scripts/test_vfs_and_script.sh
./scripts/test_missing_script.sh
./scripts/test_vfs_minimal.sh
./scripts/test_vfs_multi.sh
./scripts/test_vfs_deep.sh
./scripts/test_vfs_missing.sh
./scripts/test_vfs_invalid.sh
./scripts/test_vfs_duplicate.sh
```

### Запуск тестов

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

После запуска введите команду в нижнее поле и нажмите Enter.

```
minimal$ ls
ls

minimal$ vfs-tree
/
/only.txt  [file]

minimal$ conf-dump
vfs_path=examples/vfs/minimal.xml
startup_script=
vfs_name=minimal
vfs_loaded=yes
```

### Ошибка загрузки VFS

```
deep$ 
vfs: examples/vfs/no-such-vfs.xml: no such file
```

При неверном XML или дубликатах имён в каталоге выводится
`vfs: ...: invalid XML format` или `vfs: ...: invalid format: ...`.

### Стартовый скрипт этапа 3

Файл `examples/startup_stage3.script` — команды этапов 1–3,
`vfs-tree`, ошибочная команда и `conf-dump`.

```
deep$ conf-dump
...
deep$ vfs-tree /level1/level2/level3
/level1/level2/level3
/level1/level2/level3/leaf.txt  [file]
deep$ unknown-cmd
unknown-cmd: command not found
script error: unknown-cmd: command not found
```
