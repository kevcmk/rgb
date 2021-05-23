# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get install -y \
  build-essential

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Cloned from https://github.com/hzeller/rpi-rgb-led-matrix.git
COPY rpi-rgb-led-matrix rpi-rgb-led-matrix
WORKDIR /app/rpi-rgb-led-matrix
RUN make -C examples-api-use
RUN make install-python

WORKDIR /app
COPY . .

# CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
CMD [ "rpi-rgb-led-matrix/examples-api-use/demo", "-D0" ]
