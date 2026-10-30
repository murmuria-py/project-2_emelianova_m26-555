import shlex

from prettytable import PrettyTable

from .constants import META_FILE, PROMPT, WELCOME_TEXT
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    matches,
    select,
    update,
)
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(data):
    """Печатает список записей в виде таблицы."""
    if not data:
        print("Нет данных.")
        return
    table = PrettyTable()
    table.field_names = list(data[0].keys())
    for record in data:
        table.add_row(list(record.values()))
    print(table)


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


def parse_condition(args):
    """Разбирает ['age', '=', '28'] в ({'age': '28'}, None).
    Возвращает (dict, None) или (None, 'сообщение об ошибке')."""
    if len(args) != 3:
        return None, "Некорректное значение. Попробуйте снова."
    col, op, value = args
    if op != "=":
        return None, "Некорректное значение. Попробуйте снова."
    return {col: value}, None


def parse_values(raw_args):
    """Разбирает ['(Sergei,', '28,', 'true)'] в (['Sergei', '28', 'true'], None).
    Возвращает (list, None) или (None, 'сообщение об ошибке')."""
    if not raw_args:
        return None, "Некорректное значение. Попробуйте снова."
    raw = " ".join(raw_args)
    raw = raw.strip("()")
    values = [v.strip() for v in raw.split(",")]
    return values, None


def handle_insert(metadata, args):
    """Обрабатывает insert into <table> values (...)."""
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        return metadata, "Некорректное значение. Попробуйте снова."

    table_name = args[2]
    values, err = parse_values(args[4:])
    if err is not None:
        return metadata, err

    table_data, err = insert(metadata, table_name, values)
    if err is not None:
        return metadata, err

    save_table_data(table_name, table_data)
    record_id = table_data[-1]["ID"]   # ID последней добавленной записи
    print(f'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".')
    return metadata, None


def handle_select(metadata, args):
    """Обрабатывает select from <table> [where <col> = <value>]."""
    if len(args) < 3 or args[1] != "from":
        return metadata, "Некорректное значение. Попробуйте снова."

    table_name = args[2]
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'

    where_clause = None
    if len(args) > 3:
        if args[3] != "where":
            return metadata, "Некорректное значение. Попробуйте снова."
        where_clause, err = parse_condition(args[4:])
        if err is not None:
            return metadata, err

    table_data = load_table_data(table_name)
    filtered, err = select(table_data, where_clause)
    if err is not None:
        return metadata, err

    print_table(filtered)
    return metadata, None


def handle_update(metadata, args):
    """Обрабатывает update <table> set <col> = <val> where <col> = <val>."""
    if len(args) < 7 or args[2] != "set" or args[6] != "where":
        return metadata, "Некорректное значение. Попробуйте снова."

    table_name = args[1]
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'

    set_clause, err = parse_condition(args[3:6])
    if err is not None:
        return metadata, err

    where_clause, err = parse_condition(args[7:])
    if err is not None:
        return metadata, err

    table_data = load_table_data(table_name)
    matched_ids = [r["ID"] for r in table_data if matches(r, where_clause)]

    table_data, err = update(table_data, set_clause, where_clause)
    if err is not None:
        return metadata, err

    save_table_data(table_name, table_data)
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')
    return metadata, None


def handle_delete(metadata, args):
    """Обрабатывает delete from <table> where <col> = <val>."""
    if len(args) < 6 or args[1] != "from" or args[3] != "where":
        return metadata, "Некорректное значение. Попробуйте снова."

    table_name = args[2]
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'

    where_clause, err = parse_condition(args[4:])
    if err is not None:
        return metadata, err

    table_data = load_table_data(table_name)
    matched_ids = [r["ID"] for r in table_data if matches(r, where_clause)]

    table_data, err = delete(table_data, where_clause)
    if err is not None:
        return metadata, err

    save_table_data(table_name, table_data)
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')
    return metadata, None


def handle_info(metadata, args):
    """Обрабатывает info <table>."""
    if len(args) < 2:
        return metadata, "Некорректное значение. Попробуйте снова."

    table_name = args[1]
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'

    columns = metadata[table_name]
    columns_repr = ", ".join(f'{c["name"]}:{c["type"]}' for c in columns)
    table_data = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_repr}")
    print(f"Количество записей: {len(table_data)}")
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
        elif command == "insert":
            metadata, err = handle_insert(metadata, args)
        elif command == "select":
            metadata, err = handle_select(metadata, args)
        elif command == "update":
            metadata, err = handle_update(metadata, args)
        elif command == "delete":
            metadata, err = handle_delete(metadata, args)
        elif command == "info":
            metadata, err = handle_info(metadata, args)
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
