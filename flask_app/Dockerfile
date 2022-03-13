FROM python:3.9

RUN mkdir -p /deploy/flask_app

WORKDIR /deploy/flask_app

COPY requirements.txt /deploy/flask_app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /deploy/flask_app
