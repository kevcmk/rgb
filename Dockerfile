FROM debian:10

RUN apt-get update && apt-get install -y build-essential

COPY ./rpi-rgb-led-matrix /code/rpi-rgb-led-matrix

WORKDIR /code/rpi-rgb-led-matrix

RUN make -C examples-api-use


# Python
RUN apt-get install python3-dev python3-pillow -y
RUN make build-python PYTHON=$(which python3)
# RUN make install-python PYTHON=$(which python3)

