FROM python:3.12-alpine

ENV LANG=en_US.UTF-8 LC_ALL=C.UTF-8 LANGUAGE=en_US.UTF-8
WORKDIR /usr/src/app

COPY apkd/ .
RUN pip install --no-cache-dir .

ENTRYPOINT [ "apkd" ]