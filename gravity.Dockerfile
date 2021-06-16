# syntax=docker/dockerfile:1

FROM kevinkatz/pi-matrix:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/rgb /app/rgb

ENV PYTHONPATH "/app/rpi-rgb-led-matrix/bindings/python/samples/:${PYTHONPATH}"

# invoke docker with -p 54321:54321 to prevent multiple concurrent runs.
EXPOSE 54321

# CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
CMD [ "python3", "rgb/basematrix.py", "--led-chain=2", "--led-slowdown-gpio=2", "--led-pixel-mapper=Rotate:270", "--form=gravity", "--max-fps=60"]
