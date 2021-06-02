# syntax=docker/dockerfile:1

FROM kevinkatz/pi-matrix:latest

WORKDIR /app/rpi-rgb-led-matrix/bindings/python/samples/

COPY rgb.py .

# invoke docker with -p 54321:54321 to prevent multiple concurrent runs.
EXPOSE 54321

# CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
CMD [ "python3", "rgb.py", "--led-chain=2", "--led-slowdown-gpio=2" ]
