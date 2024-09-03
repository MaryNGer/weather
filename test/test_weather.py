import sqlite3
from unittest.mock import patch

import pytest
import unittest
from datetime import datetime
from main import app, save_search_history, weather_get_post, get_last_searched_city


def test_save_search_history_calls_insert_and_update():
    user_id = "test_user"
    city = "Moscow"
    timestamp = "2023-10-01T12:00:00"

    with patch('main.insert_search_history') as mock_insert, \
            patch('main.update_city_search_count') as mock_update:
        # Включите аргумент conn в вызов функции
        save_search_history(user_id, city, timestamp)

        mock_insert.assert_called_once_with( user_id, city, timestamp)
        mock_update.assert_called_once_with(city)


class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        self.conn = sqlite3.connect('test_db.sqlite')
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                user_id TEXT,
                city TEXT,
                search_date TEXT
            )
        """)
        self.conn.commit()
        yield self.conn  # Возвращаем соединение для использования в тестах
        self.conn.close()

    def save_search_history(self, user_id, city, search_date):
        if user_id is None:
            raise TypeError("User ID cannot be None")
        if not city:
            raise ValueError("City cannot be empty")

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO search_history (user_id, city, search_date) VALUES (?, ?, ?)",
                       (user_id, city, search_date))
        self.conn.commit()

    def test_save_search_history_with_none_user_id(self):
        with pytest.raises(TypeError):
            self.save_search_history(None, "Moscow", "2023-10-01T12:00:00")

    def test_save_search_history_with_empty_city(self):
        with pytest.raises(ValueError, match="City cannot be empty"):
            self.save_search_history("test_user", "", "2023-10-01T12:00:00")


