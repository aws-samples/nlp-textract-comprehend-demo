FROM python:3.6-alpine

LABEL maintainer="Lucas Duarte"

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN apk update && apk add docker

COPY . /app
WORKDIR /app

ENTRYPOINT ["python", "-u", "setup.py"]