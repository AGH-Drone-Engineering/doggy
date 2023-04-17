import paho.mqtt.client as mqtt
import struct
import time
from enum import Enum


BROKER_ADDRESS = "192.168.12.1"
BROKER_PORT = 1883


class DoggyAction(Enum):
    STAND_UP = "standUp"
    STAND_DOWN = "standDown"
    RUN = "run"
    WALK = "walk"
    CLIMB = "climb"


class Doggy:
    def __init__(self, wait: bool = True):
        self.is_connected = False
        self.client = mqtt.Client("Doggy")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        self.client.loop_start()

        if wait:
            self.wait_for_connection()

    def wait_for_connection(self):
        while not self.is_connected:
            time.sleep(0.1)

    def send_stick(self, lx: float, ly: float, rx: float, ry: float):
        payload = struct.pack('ffff', lx, rx, ry, ly)
        self.client.publish("controller/stick", payload, qos=2)

    def send_action(self, action: DoggyAction):
        self.client.publish("controller/action", action.value, qos=2)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code {0}".format(str(rc)))
        self.is_connected = True

    def on_message(self, client, userdata, msg):
        pass
