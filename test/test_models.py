import os
import sqlite3
import unittest
from models import (create_search_history_table, create_city_counts_table, db_path, insert_search_history,
                    get_last_searched_city, update_city_count)
from datetime import datetime


class TestWeatherHistory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем временную базу данных перед тестами
        create_search_history_table()
        create_city_counts_table()

    @classmethod
    def tearDownClass(cls):
        # Удаляем временную базу данных после тестов
        os.remove(db_path)

    def test_insert_and_get_last_searched_city(self):
        user_id = "user1"
        city1 = "London"
        city2 = "Paris"
        timestamp1 = datetime.now().isoformat()
        timestamp2 = datetime.now().isoformat()

        # Вставляем данные
        insert_search_history(user_id, city1, timestamp1)
        insert_search_history(user_id, city2, timestamp2)

        # Проверяем, что последние искомые города возвращаются корректно
        last_searched = get_last_searched_city(user_id)
        self.assertEqual(len(last_searched), 2)
        self.assertEqual(last_searched[0][0], city2)  # последний город
        self.assertEqual(last_searched[1][0], city1)  # предпоследний город

    def test_update_city_count(self):
        city = "Berlin"

        # Проверяем, что город не существует
        self.assertIsNone(get_last_searched_city("user2"))

        # Обновляем счетчик для города
        update_city_count(city)

        # Проверяем, что город добавился с правильным счетчиком
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count FROM city_counts WHERE city = ?", (city,))
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

        # Обновляем счетчик еще раз
        update_city_count(city)

        # Проверяем, что счетчик увеличился
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count FROM city_counts WHERE city = ?", (city,))
            result = cursor.fetchone()
            self.assertEqual(result[0], 2)


if __name__ == '__main__':
    unittest.main()