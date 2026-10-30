# Primitive DB

Консольная база данных на Python — учебный проект. Реализует управление таблицами (создание, удаление, просмотр), хранение метаданных в JSON и установку как самостоятельный CLI-пакет.

## Возможности

- `create_table` — создание таблицы с автоматическим добавлением столбца `ID:int`
- `list_tables` — список всех таблиц
- `drop_table` — удаление таблицы
- Поддерживаемые типы данных: `int`, `str`, `bool`

## Установка

Требуется [uv](https://docs.astral.sh/uv/).

```bash
# клонировать репозиторий и перейти в него
git clone https://github.com/murmuria-py/project-2_emelianova_m26-555.git
cd project-2_emelianova_m26-555

# установить зависимости и пакет в виртуальное окружение
uv sync

# собрать пакет
uv build

# установить как глобальный CLI-инструмент
uv tool install dist/primitive_db-0.1.0-py3-none-any.whl
```

Если команда `database` не находится после установки, выполните
`uv tool update-shell` и перезапустите терминал.

## Запуск

```bash
database
```

Появится приглашение:

```
***База данных***

***Процесс работы с таблицей***
Функции:
...
>>>Введите команду: _
```

## Управление таблицами

### Команды

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец1:тип> ...` | Создать таблицу. Столбец `ID:int` добавляется автоматически первым |
| `list_tables` | Показать список всех таблиц |
| `drop_table <имя>` | Удалить таблицу |
| `help` | Справка |
| `exit` | Выход |

Поддерживаемые типы данных: `int`, `str`, `bool`.

### Пример

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: create_table users name:str
Ошибка: Таблица "users" уже существует.

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.

>>>Введите команду: drop_table products
Ошибка: Таблица "products" не существует.
```

### Демонстрация

[demo 1](https://asciinema.org/a/qJpDppdPIlJTXdJD)

## Структура проекта

```
src/primitive_db/
├── __init__.py
├── main.py       # точка входа
├── engine.py     # цикл, парсинг команд, обработчики
├── core.py       # бизнес-логика (create_table, drop_table, list_tables)
├── utils.py      # работа с файлами (load_metadata, save_metadata)
└── constants.py  # константы (META_FILE, VALID_TYPES, PROMPT, WELCOME_TEXT)
```

## Качество кода

```bash
uv run ruff check .
```

## Лицензия

Учебный проект.



