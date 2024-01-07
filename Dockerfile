FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y vim

COPY . .

RUN pip install --upgrade pip setuptools

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
