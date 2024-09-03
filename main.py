from datetime import datetime
from flask import Flask, render_template, request
from typing import Optional, Dict, Any
from get_weather import get_weather_data
import logging.config

from models import insert_search_history, update_city_count, get_last_searched_city, main_models

from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('main')

app: Flask = Flask(__name__)


def save_search_history(user_id: str, city: str, timestamp: str) -> None:
    """
    Функция принимает идентификатор пользователя, название города и временную метку поиска.
    Она сохраняет информацию о поиске в базе данных и обновляет счетчик поисков для данного города.
    :param user_id: Str Уникальный идентификатор пользователя, который выполняет поиск.
    :param city: Str Название города, по которому выполняется поиск.
    :param timestamp: Str Временная метка, указывающая, когда был выполнен поиск. Ожидается, что формат строки
        соответствует стандартному формату даты и времени.
    :return: None
    """
    logger.info('Start save_search_history')

    insert_search_history(user_id, city, timestamp)
    update_city_search_count(city)


def update_city_search_count(city: str) -> None:
    """
    Функция принимает название города и обновляет количество поисков,
    связанных с этим городом, в базе данных.
    :param city: (str): Название города, для которого необходимо обновить счетчик поисков.
    :return: None
    """
    update_city_count(city)


def weather_get_post(weather_result: dict, city: str) -> tuple:
    """
    Получает текущую погоду для заданного города и возвращает данные о погоде
    и последнем искомом городе.

    Функция принимает результат погодного запроса и название города,
    извлекает текущие погодные данные на основе времени и возвращает их вместе
    с информацией о последнем искомом городе.
    :param weather_result: (dict): Словарь с результатами погодного запроса, где ключом является час
        (в формате строки), а значением - информация о погоде.
    :param city: (str): Название города, для которого запрашивается информация о погоде.
    :return: (tuple):
        Кортеж, содержащий:
        - словарь с текущей погодой для указанного часа
        - исходный словарь с результатами погодного запроса
        - название последнего искомого города.

    Возможно возникновение исключений, связанных с обращением к данным,
    если структура `weather_result` не соответствует ожидаемой,
    или если возникли проблемы с получением последнего искомого города.
    """
    logger.info('Start weather_get_post')

    now_date_time = datetime.now()
    now_time_hour = str(now_date_time.time().hour)
    user_id = request.remote_addr

    last_city_records = get_last_searched_city(user_id)

    last_city = last_city_records[0][0] if last_city_records else None

    if last_city is None:
        logger.info('weather_get_post: No cities in the database')
        last_city = city

    weather_now = weather_result[now_time_hour].copy()
    weather_now['weather_code'] = weather_now['weather_code'].replace('-1', '')

    return weather_now, last_city


def get_last_city_link(user_id: str) -> dict:
    """
    Получает ссылку на последний искомый город пользователя.

    Функция обращается к базе данных, чтобы извлечь последний искомый город для
    указанного пользователя по его идентификатору. Если город найден, функция
    формирует словарь с текстом города и соответствующей ссылкой на страницу
    прогноза погоды.
    :param user_id: (str): Уникальный идентификатор пользователя, для которого нужно получить последний искомый город.
    :return: Dict: Словарь с ключами:
        - 'text' (str): Название последнего искомого города с заглавной буквы.
        - 'href' (str): URL-ссылка на страницу прогноза погоды для данного города.
        Если последний город не найден, возвращается пустой словарь.
    """

    last_city_db = get_last_searched_city(user_id)
    link_data = {}

    if last_city_db:
        last_city = last_city_db[0][0].capitalize()
        link_data['text'] = last_city
        link_data['href'] = f'/?city={last_city}'

    return link_data


def handle_get_request(link_data: dict) -> str:
    """
    Обрабатывает GET-запрос и возвращает соответствующий ответ.

    Функция проверяет наличие параметра 'city' в запросе. Если параметр 'city'
    присутствует, функция извлекает его значение и вызывает функцию для получения
    данных о погоде для указанного города. Если параметра 'city' нет, функция
    возвращает основной шаблон с переданными данными ссылки.
    :param link_data: (dict): Словарь, содержащий текст и ссылку на последний искомый город.
    :return: Str: HTML-контент, который будет возвращен в ответ на запрос.
    """

    logger.info('Start handle_get_request')

    if 'city' in request.args:

        logger.info('There is a city parameter')

        city_request = request.args.get('city')
        return fetch_weather_data(city_request, link_data)

    logger.info('There is no city parameter in the request, return base.html')

    return render_template('base.html', link_data=link_data)


def handle_post_request(user_id: str, link_data: dict) -> str:
    """
    Обрабатывает POST-запрос и возвращает соответствующий ответ.

    Эта функция извлекает название города из данных формы POST-запроса и
    вызывает функцию для получения данных о погоде для указанного города.
    Также передает идентификатор пользователя и данные ссылки.
    :param user_id: (str): Уникальный идентификатор пользователя, который отправил запрос.
    :param link_data: (dict): Словарь, содержащий текст и ссылку на последний искомый город.
    :return: Str: HTML-контент, который будет возвращен в ответ на запрос.
    """
    logger.info('Start handle_post_request')
    city_request = request.form['city']

    return fetch_weather_data(city_request, link_data, user_id)


def fetch_weather_data(city_request: str, link_data: Dict[str, str], user_id: Optional[str] = None) -> Any:
    """
    Получает данные о погоде для указанного города и возвращает HTML-страницу с результатами.

    :param city_request: (str): Название города, для которого запрашиваются данные о погоде.
    :param link_data: (Dict[str, str]): Словарь, содержащий данные для ссылки на последний искомый город.
        Должен содержать ключи 'text' и 'href'.
    :param user_id: (Необязательный): Идентификатор пользователя для сохранения истории поиска.
    :return: HTML-шаблон с данными о погоде или сообщение об ошибке, если город не найден.
    """

    logger.info('Start fetch_weather_data')

    result = get_weather_data(city_request)

    if result is None:
        logger.info('City not found')

        return render_template('get_weather.html', error_message="Город не найден", link_data=link_data)

    weather_now, last_city = weather_get_post(result, city_request)

    if user_id:
        save_search_history(user_id, city_request, datetime.now().isoformat())  # Сохраняем историю поиска
        link_data['text'] = last_city.capitalize()
        link_data['href'] = f'/?city={last_city}'

    logger.info('fetch_weather_data: Render get_weather.html')

    return render_template('get_weather.html', city=city_request.capitalize(),
                           weather_now=weather_now, weather_data=result, link_data=link_data)


@app.route('/', methods=["GET", "POST"])
def weather():
    try:
        user_id = request.remote_addr
        link_data = get_last_city_link(user_id)

        if request.method == 'GET':
            logger.info('Start processing GET request')
            return handle_get_request(link_data)

        if request.method == 'POST':
            logger.info('Start processing POST request')
            return handle_post_request(user_id, link_data)

        return render_template('base.html', link_data=link_data)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}, code: 500")
        return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    main_models()
    app.run(debug=True, host='0.0.0.0', port=5000)
