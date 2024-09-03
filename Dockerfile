FROM python:3.10-slim

RUN mkdir /app

COPY requirements.txt /app/

RUN python -m pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]

