FROM --platform=linux/arm64 python:3.9

RUN mkdir -p /deploy/flask_app

WORKDIR /deploy/flask_app

# install google chrome
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y chromium chromium-driver

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY ./pokemon_data_scraper/requirements.txt /deploy/flask_app/pokemon_data_scraper/requirements.txt
RUN pip install --no-cache-dir -r pokemon_data_scraper/requirements.txt

COPY ./flask_app/requirements.txt /deploy/flask_app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./pokemon_data_scraper/ /deploy/flask_app/pokemon_data_scraper

COPY ./flask_app /deploy/flask_app
