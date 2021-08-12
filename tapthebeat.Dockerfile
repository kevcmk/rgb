FROM debian:10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y build-essential python3-all-dev python3-pip python3-numpy python3-pillow

WORKDIR /app

COPY requirements.txt .

RUN apt-get install -y portaudio19-dev
RUN pip3 install pyaudio numpy==1.20.3 paho-mqtt==1.5.1 aubio==0.4.9

ENV PYTHONPATH ".:${PYTHONPATH}"

COPY src/rgb /app/rgb
COPY aubiodemos /app/aubiodemos

# invoke docker with -p 54322:54322 to prevent multiple concurrent runs.
EXPOSE 54322

CMD [ "python3", "aubiodemos/demo_pyaudio.py" ]
