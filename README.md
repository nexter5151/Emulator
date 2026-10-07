# Shell Emulator

## 1. Общее описание

Эмулятор командной оболочки UNIX-подобной ОС (вариант №4).
Реализованы этапы 1–5: REPL в GUI, параметры командной строки,
стартовый скрипт, VFS из XML в памяти, команды `ls`, `cd`, `cat`,
`rev`, `du`, `mkdir`, `help`, служебные `conf-dump` и `vfs-tree`.

Язык реализации: Python 3.
Интерфейс: tkinter (стандартная библиотека).

## 2. Функции и настройки

### Модули

| Файл | Назначение |
|------|------------|
| `src/main.py` | Точка входа, создание runtime и запуск GUI |
| `src/gui.py` | Графический интерфейс (окно, ввод, вывод) |
| `src/parser.py` | Парсер: разбивает строку на команду и аргументы |
| `src/commands.py` | Команды оболочки и служебные команды |
| `src/config.py` | Параметры командной строки и отладочный вывод |
| `src/runtime.py` | Состояние: config, VFS, текущий каталог cwd |
| `src/vfs.py` | Модель VFS, XML, пути, размеры, mkdir |
| `src/script_runner.py` | Чтение и выполнение стартового скрипта |

### Формат XML VFS

Корневой элемент — `<vfs name="имя">`. Внутри — вложенные
`<directory name="...">` и
`<file name="..." encoding="text|base64">`.
Текст файла — тело элемента; для двоичных данных — base64.
Данные только в памяти, исходный файл на диске не изменяется.
Команда `mkdir` тоже меняет только память.

Примеры: `examples/vfs/minimal.xml`, `multi.xml`, `deep.xml`,
`unix.xml`.

### Описание функций (этап 5)

#### `src/vfs.py`

| Имя | Назначение |
|-----|------------|
| `create_directory(vfs, path, parents)` | Создание каталога в памяти; `-p` через `parents`. |
| `normalize_path(cwd, path)` | Абсолютный путь с `.`, `..` и относительными сегментами. |
| `resolve_path(vfs, path)` | Поиск узла по абсолютному пути. |
| `node_size` / `human_size` | Размеры для `ls -lh` и `du`. |

#### `src/commands.py` (этап 5)

| Имя | Назначение |
|-----|------------|
| `mkdir [-p] path…` | Создать каталог(и) только в памяти. |
| `help [cmd…]` | Список команд и краткие описания. |

### Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `--vfs PATH` | Путь к XML-файлу VFS |
| `--script PATH` | Путь к стартовому скрипту |

При запуске выводится блок `[config]`. Без `--vfs` имя —
`stub-vfs`. Приглашение: `имя_vfs:cwd$`.

### Команды эмулятора

| Команда | Описание |
|---------|----------|
| `ls [-alh] [path…]` | Содержимое каталога; `-a`, `-l`, `-h` |
| `cd [path]` | Смена текущего каталога VFS |
| `cat file…` | Печать файла |
| `rev file…` | Печать файла с реверсом строк |
| `du [-h] [path…]` | Размер в байтах или human-readable |
| `mkdir [-p] path…` | Создать каталог (только в памяти) |
| `help [cmd…]` | Справка по командам |
| `conf-dump` | Параметры эмулятора и статус VFS |
| `vfs-tree [path]` | Дерево каталогов VFS |
| `exit` | Завершение работы |

Неизвестная команда: `<команда>: command not found`.

## 3. Сборка и запуск

Сборка не требуется — только стандартная библиотека Python.

### Запуск приложения

```bash
./run.sh
```

```bash
python3 -m src.main \
  --vfs examples/vfs/unix.xml \
  --script examples/startup_stage5.script
```

### Скрипты проверки

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
./scripts/test_stage4.sh
./scripts/test_stage5.sh
```

### Запуск тестов

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

```
unix:/$ help
ls — list directory contents (-a, -l, -h)
...
mkdir — create directory (-p for parents)
help — show this command list

unix:/$ mkdir newdir
unix:/$ mkdir -p deep/a/b/c
unix:/$ ls deep/a/b
c

unix:/$ cd home/user/data
unix:/home/user/data$ cat notes.txt
hello world
line two
```

### Обработка ошибок

```
unix:/$ mkdir home
mkdir: cannot create directory 'home': File exists

unix:/$ mkdir no/such
mkdir: cannot create directory 'no/such': No such file or directory

unix:/$ help nope
help: no help for 'nope'
```

### Стартовые скрипты

- этап 4: `examples/startup_stage4.script`
- этап 5: `examples/startup_stage5.script` — `help`, `mkdir`,
  `-p`, ошибки и `vfs-tree`
