FROM python:3.9

RUN mkdir -p /deploy/flask_app

WORKDIR /deploy/flask_app

COPY ./flask_app/requirements.txt /deploy/flask_app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./pokemon_data_scraper /deploy/flask_app/pokemon_data_scraper
COPY ./flask_app /deploy/flask_app
