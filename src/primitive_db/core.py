from .constants import VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создает таблицу. Возвращает (metadata, None) или (None, 'ошибка')."""
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
    """Удаляет таблицу. Возвращает (metadata, None) или (None, 'ошибка')."""
    if table_name not in metadata:
        return None, f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata[table_name]
    return metadata, None

def list_tables(metadata):
    """Возвращает список таблиц."""
    return list(metadata.keys())