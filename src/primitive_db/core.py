from .constants import VALID_TYPES
from .utils import load_table_data


def create_table(metadata, table_name, columns):
    """Создает таблицу. 
    Возвращает (metadata, None) или (None, 'ошибка')."""
    if table_name in metadata:
        return None, f'Ошибка: Таблица "{table_name}" уже существует.'

    for col in columns:
        if col["type"] not in VALID_TYPES:
            return None, (
                f'Некорректное значение: тип "{col["type"]}" '
                f'для столбца "{col["name"]}". Попробуйте снова.'
            )
        if col["name"] == "ID" and col["type"] != "int":
            return None, (
                f'Некорректное значение: столбец ID должен иметь тип int, '
                f'получен "{col["type"]}". Попробуйте снова.'
            )

    if not any(col["name"] == "ID" for col in columns):
        columns.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = columns
    return metadata, None


def drop_table(metadata, table_name):
    """Удаляет таблицу. 
    Возвращает (metadata, None) или (None, 'ошибка')."""
    if table_name not in metadata:
        return None, f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata[table_name]
    return metadata, None


def list_tables(metadata):
    """Возвращает список таблиц."""
    return list(metadata.keys())


def insert(metadata, table_name, values):
    """Добавляет запись в таблицу. 
    Возвращает (table_data, None) или (None, 'ошибка')."""
    if table_name not in metadata:
        return None, f'Ошибка: Таблица "{table_name}" не существует.'

    columns = metadata[table_name]
    expected = len(columns) - 1
    if len(values) != expected:
        return None, (
            f"Некорректное значение: ожидалось {expected} значений, "
            f"получено {len(values)}. Попробуйте снова."
        )

    record = {"ID": None}
    for col, raw in zip(columns[1:], values):
        name, type_ = col["name"], col["type"]
        if type_ == "int":
            try:
                record[name] = int(raw)
            except ValueError:
                return None, (
                    f'Некорректное значение: "{raw}" не является int '
                    f'для столбца "{name}". Попробуйте снова.'
                )
        elif type_ == "bool":
            lowered = raw.lower()
            if lowered not in ("true", "false"):
                return None, (
                    f'Некорректное значение: "{raw}" не является bool '
                    f'для столбца "{name}". Попробуйте снова.'
                )
            record[name] = lowered == "true"
        else:  # str
            record[name] = raw

    table_data = load_table_data(table_name)
    record["ID"] = max((r["ID"] for r in table_data), default=0) + 1
    table_data.append(record)
    return table_data, None


def matches(record, where_clause):
    """Проверяет, удовлетворяет ли запись условию where_clause."""
    for col, value in where_clause.items():
        record_val = record[col]
        if isinstance(record_val, bool):
            if str(record_val).lower() != str(value).lower():
                return False
        elif str(record_val) != str(value):
            return False
    return True


def select(table_data, where_clause=None):
    """Возвращает записи по условию 
    (или все, если условие не задано)."""
    if where_clause is None:
        return table_data, None

    filtered = [record for record in table_data if matches(record, where_clause)]
    return filtered, None


def update(table_data, set_clause, where_clause):
    """Обновляет записи по условию. 
    Возвращает (table_data, None) или (None, 'ошибка')."""
    updated = 0
    for record in table_data:
        if not matches(record, where_clause):
            continue
        for col, value in set_clause.items():
            current = record[col]
            if isinstance(current, bool):
                lowered = str(value).lower()
                if lowered not in ("true", "false"):
                    return None, (
                        f'Некорректное значение: "{value}" не является bool '
                        f'для столбца "{col}". Попробуйте снова.'
                    )
                record[col] = lowered == "true"
            elif isinstance(current, int):
                try:
                    record[col] = int(value)
                except ValueError:
                    return None, (
                        f'Некорректное значение: "{value}" не является int '
                        f'для столбца "{col}". Попробуйте снова.'
                    )
            else:
                record[col] = value
        updated += 1
    if updated == 0:
        return None, "Некорректное значение: записей не найдено. Попробуйте снова."
    return table_data, None


def delete(table_data, where_clause):
    """Удаляет записи по условию. 
    Возвращает (table_data, None) или (None, 'ошибка')."""
    filtered = [record for record in table_data if not matches(record, where_clause)]
    if len(filtered) == len(table_data):
        return None, "Некорректное значение: записей не найдено. Попробуйте снова."
    return filtered, None

