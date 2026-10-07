# Shell Emulator

## 1. Общее описание

Эмулятор командной оболочки UNIX-подобной ОС (вариант №4).
Реализованы этапы 1–4: REPL в GUI, параметры командной строки,
стартовый скрипт, VFS из XML в памяти, команды `ls`, `cd`, `cat`,
`rev`, `du`, служебные `conf-dump` и `vfs-tree`.

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
| `src/vfs.py` | Модель VFS, XML, пути, размеры |
| `src/script_runner.py` | Чтение и выполнение стартового скрипта |

### Формат XML VFS

Корневой элемент — `<vfs name="имя">`. Внутри — вложенные
`<directory name="...">` и
`<file name="..." encoding="text|base64">`.
Текст файла — тело элемента; для двоичных данных — base64.
Данные только в памяти, исходный файл на диске не изменяется.

Примеры: `examples/vfs/minimal.xml`, `multi.xml`, `deep.xml`,
`unix.xml` (для этапа 4: `home/user/data`).

### Описание функций (этап 4)

#### `src/vfs.py`

| Имя | Назначение |
|-----|------------|
| `normalize_path(cwd, path)` | Абсолютный путь с учётом `.`, `..` и относительных сегментов. |
| `resolve_path(vfs, path)` | Поиск узла по абсолютному пути. |
| `node_size(node)` | Размер файла или сумма содержимого каталога. |
| `human_size(size)` | Размер в виде `12B`, `1.5K`, … |
| `format_tree(vfs, start)` | Дерево каталогов для `vfs-tree`. |

#### `src/runtime.py`

| Имя | Назначение |
|-----|------------|
| `EmulatorRuntime` | Config, VFS, ошибка загрузки, `cwd`. |
| `absolute_path(path)` | Путь относительно текущего каталога. |
| `lookup(path)` | Поиск узла по относительному/абсолютному пути. |
| `format_conf_dump()` | Параметры + `cwd` + статус VFS. |

#### `src/commands.py` (этап 4)

| Имя | Назначение |
|-----|------------|
| `ls [-alh] [path…]` | Список каталога/файла; флаги `-a`, `-l`, `-h` и комбинации. |
| `cd [path]` | Смена каталога; относительные пути и `..`. |
| `cat file…` | Вывод содержимого файла. |
| `rev file…` | Реверс символов в каждой строке файла. |
| `du [-h] [path…]` | Размер файла/каталога. |

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
| `ls [-alh] [path…]` | Содержимое каталога; `-a` скрытые, `-l` подробно, `-h` размеры |
| `cd [path]` | Смена текущего каталога VFS |
| `cat file…` | Печать файла |
| `rev file…` | Печать файла с реверсом строк |
| `du [-h] [path…]` | Размер в байтах или human-readable |
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
  --script examples/startup_stage4.script
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
```

### Запуск тестов

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

```
unix:/$ ls
home
readme.txt
tmp

unix:/$ ls -la home/user
drwxr-xr-x        0 .
drwxr-xr-x        0 ..
-rw-r--r--       16 .bashrc
drwxr-xr-x       … data
-rw-r--r--       11 profile.txt

unix:/$ cd home/user/data
unix:/home/user/data$ cat notes.txt
hello world
line two

unix:/home/user/data$ rev notes.txt
dlrow olleh
owt enil

unix:/home/user/data$ ls -lh
-rw-r--r--      12B .hidden
-rw-r--r--      18B notes.txt
-rw-r--r--       6B secret.bin

unix:/home/user/data$ du -h
…	/home/user/data
```

### Обработка ошибок

```
unix:/$ cd no/such
cd: no/such: No such file or directory

unix:/$ cd readme.txt
cd: readme.txt: Not a directory

unix:/$ cat missing.txt
cat: missing.txt: No such file or directory

unix:/$ ls -z
ls: invalid option -- 'z'
```

### Стартовый скрипт этапа 4

Файл `examples/startup_stage4.script` — режимы `ls`/`cd`/`cat`/
`rev`/`du`, вложенные пути и ошибки.
