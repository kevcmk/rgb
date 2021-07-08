FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip3 install rpi_ws281x

COPY src/rgb /app/rgb

# invoke docker with -p 54322:54322 to prevent multiple concurrent runs.
EXPOSE 54322

CMD [ "python3", "rgb/rgb1d.py" ]
