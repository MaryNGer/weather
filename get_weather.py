import logging.config
import openmeteo_requests
import pandas as pd
import requests_cache
from geopy.geocoders import Nominatim
from requests import RequestException
from retry_requests import retry
from config import user_agent_api
import certifi
import ssl

from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('get_weather')

ssl_context = ssl.create_default_context(cafile=certifi.where())


def get_is_day(is_day: int) -> str:
    """
     Функция возвращает строку, описывающую, является ли сейчас день или ночь.

    :param is_day: Целое число, где 0 означает ночь (темно), а 1 означает день (светло).
    :return: Str: Строка, описывающая текущее время суток.
    """
    num_day = {
        0: "темно",
        1: "светло"
    }

    if is_day in num_day:
        return num_day[is_day]


def get_weather_code(weather_cod: int, is_day: int) -> str:
    """
    Функция возвращает путь к SVG-изображению, соответствующему заданному коду погоды и времени суток.

    :param weather_cod: Код погоды, который определяет тип погоды.
    :param is_day: Целое число, где 0 означает ночь, а 1 означает день.
    :return: Str: Путь к SVG-изображению, соответствующему заданному коду погоды и времени суток.
    """
    logger.info('Start get_weather_code')

    weather_codes = {
        0: '../static/img/clear_day-1.svg',
        1: '../static/img/clear_day-1.svg',
        2: '../static/img/clear_day-1.svg',
        3: '../static/img/clear_day-1.svg',
        45: '../static/img/fog-1.svg',
        48: '../static/img/fog-1.svg',
        51: '../static/img/cloud-1.svg',
        53: '../static/img/cloud-1.svg',
        55: '../static/img/cloud-1.svg',
        56: '../static/img/rainy-1.svg',
        57: '../static/img/rainy-1.svg',
        61: '../static/img/rainy-1.svg',
        63: '../static/img/rainy-1.svg',
        65: '../static/img/rainy-1.svg',
        66: '../static/img/rainy-1.svg',
        67: '../static/img/rainy-1.svg',
        71: '../static/img/cloudy_snowing-1.svg',
        73: '../static/img/cloudy_snowing-1.svg',
        75: '../static/img/cloudy_snowing-1.svg',
        77: '../static/img/cloudy_snowing-1.svg',
        80: '../static/img/rainy-1.svg',
        81: '../static/img/rainy-1.svg',
        82: '../static/img/rainy-1.svg',
        85: '../static/img/cloudy_snowing-1.svg',
        86: '../static/img/ac_unit-1.svg',
        95: '../static/img/thunderstorm-1.svg',
        96: '../static/img/thunderstorm-1.svg',
        99: '../static/img/thunderstorm-1.svg'
    }

    if weather_cod in weather_codes:
        if weather_cod < 4 and is_day == 0:
            for i in range(4):
                weather_codes[i] = '../static/img/bedtime-1.svg'
        elif weather_cod < 4 and is_day == 1:
            for i in range(4):
                weather_codes[i] = '../static/img/clear_day-1.svg'

        return weather_codes[weather_cod]
    else:
        return '../static/img/clear_day-1.svg'


def get_weather(lat: float, long: float) -> dict:
    """
    Получает данные о погоде для заданных координат (широта и долгота) на ближайшие 24 часа.

    :param lat: Широта в градусах (-90 до 90).
    :param long: Долгота в градусах (-180 до 180).
    :return: Словарь с данными о погоде на каждый час на ближайшие 24 часа.
              Каждый ключ в словаре представляет собой строку с часом (например, '00', '01', ...),
              а значение - словарь с данными о погоде для этого часа.

    Raises:
        ValueError: Если значения широты или долготы находятся вне допустимых диапазонов.
        RequestException: Если произошла ошибка при запросе к API Open-Meteo.
        KeyError: Если произошла ошибка при обработке данных.
        Exception: Если произошла другая непредвиденная ошибка.
    """

    logger.info('Start get_weather')

    if not (-90 <= lat <= 90 and -180 <= long <= 180):
        logger.error('Invalid latitude or longitude')
        raise ValueError("Invalid latitude or longitude")
    try:
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": long,
            "timezone": "Europe/Moscow",
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                       "precipitation_probability", "is_day", "weather_code"]
        }
        responses = openmeteo.weather_api(url, params=params)

        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
        hourly_is_day = hourly.Variables(4).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["is_day"] = hourly_is_day
        hourly_data["weather_code"] = hourly_weather_code

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        current_time = pd.Timestamp.now(tz="UTC")
        end_time = current_time + pd.DateOffset(hours=24)

        filtered_data = hourly_dataframe[
            (hourly_dataframe['date'] >= current_time) & (hourly_dataframe['date'] <= end_time)]

        weather_data = {}

        logger.info('We form a dictionary with the received data')

        for index, row in filtered_data.iterrows():
            time_str = row['date'].strftime('%H')
            temperature = int(row['temperature_2m'])
            relative_humidity = int(row['relative_humidity_2m'])
            wind_speed = int(row['wind_speed_10m'])
            precipitation_probability = int(row['precipitation_probability'])
            is_day = int(row['is_day'])
            weather_code = (int(row['weather_code']))

            weather_code = get_weather_code(weather_code, is_day)
            is_day = get_is_day(is_day)

            hourly_data = {
                "Temperature": f"{temperature}°",
                "Relative Humidity": f"{relative_humidity}%",
                "Wind Speed": f"{wind_speed} m/s",
                "Precipitation Probability": f"{precipitation_probability}%",
                "Is Day": is_day,
                'weather_code': weather_code
            }

            weather_data.update({time_str: hourly_data})

        return weather_data
    except ValueError as ve:
        logger.error(f'Invalid input: {ve}')
        raise

    except RequestException as e:
        logger.error(f'Error when requesting Open-Meteo API: {str(e)}')
        raise

    except KeyError as e:
        logger.error(f'Error while processing data: {str(e)}')
        raise

    except Exception as e:
        logger.error(f'An error has occurred: {str(e)}')
        raise


def get_weather_data(city: str) -> dict | None:
    """
    Получает широту и долготу по названию города и вызывает функцию для получения погоды.

    :param city: Название города, для которого нужно получить данные о погоде.
    :return: Dict: Словарь с данными о погоде или None, если город не найден или произошла ошибка.
    """

    logger.info('Start get_weather_data')

    if not city:
        logger.error('City name is empty or None')
        return None
    try:
        user_agent = user_agent_api

        logger.info('Create a geolocator object using: Nominatim')
        geolocator = Nominatim(user_agent=user_agent, ssl_context=ssl_context)

        logger.info('Get the coordinates of the city')
        location = geolocator.geocode(city)

        if location is None:
            logger.error('This location does not exist')
            return None

        logger.info(f'Location - {location}')

        lat = location.latitude
        long = location.longitude

        weather_data = get_weather(lat, long)

        return weather_data

    except Exception as e:
        logger.error(f'Error get_weather_data: {e}')
        return None
