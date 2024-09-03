import sqlite3
import logging.config
from sqlite3 import Cursor
from typing import Optional, List, Tuple

from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('models')

db_path = 'table_weather_history.db'


def create_search_history_table() -> None:
    """
    Создает таблицу с именем 'search_history' в базе данных SQLite, если она еще не существует.

    :return: None
    """

    try:
        with sqlite3.connect(db_path) as conn:
            cursor: Cursor = conn.cursor()

            create_table_query = """
                CREATE TABLE IF NOT EXISTS search_history
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                city TEXT, 
                search_date TIMESTAMP,
                user_id TEXT)
            """
            cursor.execute(create_table_query)
    except sqlite3.Error as e:
        logger.error(f'Error creating table city_counts: {e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


def create_city_counts_table() -> None:
    """
    Создает таблицу для хранения количества вводов городов в базе данных SQLite, если она еще не существует.

    :return: None
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor: Cursor = conn.cursor()

            create_table_query = """
                    CREATE TABLE IF NOT EXISTS city_counts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    count INTEGER)
                """
            cursor.execute(create_table_query)
    except sqlite3.Error as e:
        logger.error(f'Error creating table city_counts: {e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


def ensure_search_history_table_exists(cursor: sqlite3.Cursor) -> None:
    """
    Проверяет, существует ли таблица search_history, и создает её, если она не существует.

    :return: None
    """
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='search_history';
        """
    )
    exists: Optional[tuple[str,]] = cursor.fetchone()

    if not exists:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS search_history
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            city TEXT, 
            search_date TIMESTAMP,
            user_id TEXT)
        """
        cursor.execute(create_table_query)


def ensure_city_counts_table_exists(cursor: sqlite3.Cursor) -> None:
    """
    Проверяет, существует ли таблица city_counts, и создает её, если она не существует.

    :return: None
    """
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='city_counts';
        """
    )
    exists: Optional[tuple[str,]] = cursor.fetchone()

    if not exists:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS city_counts
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            count INTEGER)
        """
        cursor.execute(create_table_query)


def insert_search_history(user_id: str, city: str, timestamp: str):
    logger.info('Start insert_search_history')

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            ensure_search_history_table_exists(cursor)

            insert_query = """
                INSERT INTO search_history (user_id, city, search_date) VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (user_id, city, timestamp))

            conn.commit()
            logger.info(f'Successfully inserted search history for user {user_id} in city {city} at {timestamp}')
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


def update_city_count(city: str) -> None:
    """
    Обновляет счетчик вводов города в базе данных.

    Если город уже существует в таблице city_counts, увеличивает счетчик на 1.
    Если города нет в таблице, добавляет его со счетчиком 1.

    :param city: Название города.
    :return: None
    """

    logger.info('Start update_city_count')

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            ensure_city_counts_table_exists(cursor)

            cursor.execute("SELECT count FROM city_counts WHERE city = ?", (city,))
            result = cursor.fetchone()

            if result:
                count = result[0] + 1
                cursor.execute("UPDATE city_counts SET count = ? WHERE city = ?", (count, city))
            else:
                cursor.execute("INSERT INTO city_counts (city, count) VALUES (?, 1)", (city,))

            conn.commit()
            logger.info(f'Successfully updated city count for {city}')
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


def get_last_searched_city(user_id: str) -> list[tuple[str]] | None:
    """
    Получить последний искомый город из истории поиска для данного пользователя.

    Функция подключается к базе данных SQLite и выполняет запрос к истории поиска
    для получения самого последнего города, который искал указанный пользователь.
    Во время выполнения функции записывается соответствующая информация, включая
    любые ошибки, которые могут возникнуть.

    :param user_id: (str): Уникальный идентификатор пользователя, чью историю поиска запрашивают.
    :return: Union[List[Tuple[str]], None]: Список, содержащий кортеж с последним искомым городом,
        если он найден, или None, если города не найдены или произошла ошибка.
    """
    logger.info('Start get_last_searched_city')
    try:
        with sqlite3.connect(db_path) as conn:
            cursor: Cursor = conn.cursor()

            ensure_search_history_table_exists(cursor)

            select_query = """
                SELECT city FROM search_history WHERE user_id = ? ORDER BY id DESC LIMIT 1
            """
            cursor.execute(select_query, (user_id,))

            result: List[Tuple[str]] = cursor.fetchall()

            if result:
                logger.info(f'get_last_searched_city: Last city: {result[0][0]}')
                return result
            else:
                logger.info('get_last_searched_city: No cities found')
                return None
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return None


def main_models():
    create_city_counts_table()
    create_city_counts_table()


if __name__ == '__main__':
    main_models()
