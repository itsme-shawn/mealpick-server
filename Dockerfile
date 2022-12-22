FROM --platform=linux/amd64 python:3.10.8

WORKDIR /code
# 컨테이너 내 경로

COPY ./requirements.txt /code/requirements.txt

COPY ./crawler /code/crawler

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# CHROME
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/goodle.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# CHROME_DRIVER
# RUN apt-get install -yqq unzip
# RUN apt-get install -y curl
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# ENV DISPLAY=:99

RUN mkdir log