# syntax=docker/dockerfile:1

FROM kevinkatz/pi-matrix:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install scipy

# TODO Why is this a current directory? This worked previously because a colon indicates 
# a separate, and blank meant current directory
ENV PYTHONPATH ".:/app/rpi-rgb-led-matrix/bindings/python/samples/:${PYTHONPATH}"

COPY src/rgb /app/rgb

# invoke docker with -p 54321:54321 to prevent multiple concurrent runs.
EXPOSE 54321

# CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
CMD [ "python3", "rgb/mainmatrix.py"]
