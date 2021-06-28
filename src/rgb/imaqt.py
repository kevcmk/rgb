#!/usr/bin/python3

import atexit
import datetime
import json
import logging
import os
import random
import sys
from typing import Dict

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

log = logging.getLogger(__name__)


class IMAQT():

    def __str__(self):
        fields = ("server_hostname", "server_port", "username", "client_id", "keep_alive")
        return json.dumps({k: getattr(self, k) for k in fields})

    def __init__(self, server_hostname: str, server_port: int, username: str, password: str, client_id: str, keep_alive: int):
        self.server_hostname = server_hostname
        self.server_port = server_port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.keep_alive = keep_alive
        
        # Because their API eats exceptions, https://github.com/eclipse/paho.mqtt.python/issues/365
        def on_log(client, userdata, level, buff):
            log.debug(buff)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                log.info(f"Connected as {client_id}.")
            else: 
                log.error(f"Failed to connect as {str(self)}")
            
        def on_message(client, userdata, msg):
            decoded = msg.payload.decode('utf-8')
            log.info(f"Unhandled message on topic '{msg.topic}': {decoded}")

        self.client = mqtt.Client(client_id=client_id)
        self.client.enable_logger(logger=log)
        self.client.on_log = on_log  # https://github.com/eclipse/paho.mqtt.python/issues/365
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        print(self.client.suppress_exceptions)
        # self.client.will_set("public/roll", generate_payload({"message": "died"}))
        # TODO Set client id
        self.client.username_pw_set(
            username=os.environ["MOSQUITTO_USER"],
            password=os.environ["MOSQUITTO_PASSWORD"]
        )

    @staticmethod
    def factory() -> "IMAQT":
        MOSQUITTO_HOST = os.environ.get("MOSQUITTO_HOST", "magenta")
        MOSQUITTO_USER = os.environ["MOSQUITTO_USER"]
        MOSQUITTO_PASSWORD = os.environ["MOSQUITTO_PASSWORD"]
        CLIENT_ID = os.environ.get(
            "MQTT_CLIENT_ID", f"client-auto-{random.randint(0,1024)}")
        MOSQUITTO_PORT = int(os.environ.get("MOSQUITTO_PORT", "1883"))
        MOSQUITTO_KEEP_ALIVE = int(os.environ.get("MQTT_KEEP_ALIVE", "60"))

        return IMAQT(
            server_hostname=MOSQUITTO_HOST,
            server_port=MOSQUITTO_PORT,
            username=MOSQUITTO_USER,
            password=MOSQUITTO_PASSWORD,
            client_id=CLIENT_ID,
            keep_alive=MOSQUITTO_KEEP_ALIVE
        )
    
    @staticmethod
    def generate_payload(d: Dict) -> str:
        return json.dumps({
            "datetime": datetime.datetime.utcnow(),
            **d,
        })
    
    def connect(self):
        log.debug(f"Attempting to connect as {str(self)}...")
        self.client.connect(self.server_hostname, self.server_port, self.keep_alive)

        def disconnect():
            log.info("MQTT Client disconnnecting...")
            self.client.disconnect()

        atexit.register(disconnect)

        # This also works
        # publish.single(topic, generate_payload({"message": "booted"}), **auth_dict)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        log.info(f'Beginning MQTT loop thread...')
        self.client.loop_start()