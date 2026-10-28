import shlex

from .constants import META_FILE, PROMPT, WELCOME_TEXT
from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(raw_columns):
    """Разбирает ['name:str', 'age:int'] в [{'name': ..., 'type': ...}, ...].
    Возвращает (columns, None) или (None, 'сообщение об ошибке')."""
    columns = []
    for raw in raw_columns:
        if ":" not in raw:
            return None, f"Некорректное значение: {raw}. Попробуйте снова."
        name, type_ = raw.split(":", 1)
        if not name or not type_:
            return None, f"Некорректное значение: {raw}. Попробуйте снова."
        columns.append({"name": name, "type": type_})
    return columns, None


def handle_create_table(metadata, args):
    """Обрабатывает create_table. Возвращает (metadata, err)."""
    if len(args) < 2:
        return metadata, "Некорректное значение: create_table. Попробуйте снова."
    table_name = args[1]
    raw_columns = args[2:]
    if not raw_columns:
        return metadata, f"Некорректное значение: {table_name}. Попробуйте снова."

    columns, err = parse_columns(raw_columns)
    if err is not None:
        return metadata, err

    _, err = create_table(metadata, table_name, columns)
    if err is not None:
        return metadata, err
    save_metadata(META_FILE, metadata)
    columns_repr = ", ".join(f'{c["name"]}:{c["type"]}' for c in columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_repr}')
    return metadata, None


def handle_drop_table(metadata, args):
    """Обрабатывает drop_table. Возвращает (metadata, err)."""
    if len(args) < 2:
        return metadata, "Некорректное значение: drop_table. Попробуйте снова."
    table_name = args[1]
    _, err = drop_table(metadata, table_name)
    if err is not None:
        return metadata, err
    save_metadata(META_FILE, metadata)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata, None


def handle_list_tables(metadata, args):
    """Обрабатывает list_tables."""
    names = list_tables(metadata)
    if not names:
        print("Таблиц нет.")
    else:
        for name in names:
            print(f"- {name}")
    return metadata, None


def run():
    """Основной цикл программы."""
    print(WELCOME_TEXT)
    print_help()
    metadata = load_metadata(META_FILE)

    while True:
        user_input = input(PROMPT)
        args = shlex.split(user_input)

        if not args:
            continue

        command = args[0]

        if command == "create_table":
            metadata, err = handle_create_table(metadata, args)
        elif command == "drop_table":
            metadata, err = handle_drop_table(metadata, args)
        elif command == "list_tables":
            metadata, err = handle_list_tables(metadata, args)
        elif command == "help":
            print_help()
            err = None
        elif command == "exit":
            break
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
            continue

        if err is not None:
            print(err)