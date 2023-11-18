FROM python:3.8.8

MAINTAINER an4ouce "an4ouce@mail.ru"

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENV ENV_FILE=./.env

EXPOSE 5000

CMD python app.py
