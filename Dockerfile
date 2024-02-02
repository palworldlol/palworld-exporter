FROM docker.io/python:alpine

RUN apk add git

WORKDIR /usr/src/app

COPY . .
RUN pip install .
CMD [ "palworld_exporter" ]
