# weather the weather

**Web-приложение, оно же сайт, где пользователь вводит название города, и получает прогноз погоды в этом городе.**

## Установка
1. Клонируйте репозиторий.
2. Установите зависимости `pip install -r requirements.txt`
3. Запустить файл main.py

## Функции
- Демонстрация погоды по искомому городу
- Демонстрация погоды по последнему искомому пользователем городу
- Приложение не требует аутентификации и авторизации сохраняя истории по ip-адресу

## Технологии
- API GeoPy
- API OpenMetio
- Flask
- SQLite

## Описание работы
- Вводим город
- Название города передается в API GeoPy который геокодирует местоположение в широту и долготу и передает в API OpenMetio
- API OpenMetio по широте и долготе забирает данные о погоде и передает их в шаблон для HTML страницы
- После происходит запись данных в БД:  
search_history - город, дата, ip  
city_counts - город, количество запросов к этому городу  

- Для приложения готов Dockerfile для запуска приложения в контейнере 
- Сделаны автодополнение (подсказки) при вводе города 
- Сохраняется история для каждого пользователя

   
![weather_the_weather](https://github.com/user-attachments/assets/dace767e-d6aa-4bbd-8a73-6ba6616d2826)
