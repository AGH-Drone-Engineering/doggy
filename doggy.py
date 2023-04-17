import paho.mqtt.client as mqtt
import struct
import time
from enum import Enum
import math


BROKER_ADDRESS = "192.168.12.1"
BROKER_PORT = 1883
MIN_PACKET_DELAY = 1 / 100


class DoggyAction(Enum):
    STAND_UP = "standUp"
    STAND_DOWN = "standDown"
    RUN = "run"
    WALK = "walk"
    CLIMB = "climb"


class Doggy:
    def __init__(self):
        self.last_send = 0

        self.client = mqtt.Client("Doggy")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        self.client.loop_start()

    def send_stick(self, lx: float, ly: float, rx: float, ry: float):
        payload = struct.pack('ffff', lx, rx, ry, ly)
        self.timed_publish("controller/stick", payload)

    def send_action(self, action: DoggyAction):
        self.client.publish("controller/action", action.value, qos=2)

    def timed_publish(self, topic: str, payload: bytes):
        now = time.time()
        if now - self.last_send >= MIN_PACKET_DELAY:
            self.client.publish(topic, payload, qos=2)
            self.last_send = now

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code {0}".format(str(rc)))
        self.client.subscribe("controller/stick")

    def on_message(self, client, userdata, msg):
        if msg.topic == "controller/stick":
            lx, rx, ry, ly = struct.unpack('ffff', msg.payload)
            print(f"Stick = ({lx} {ly}) ({rx} {ry})")


if __name__ == "__main__":
    doggy = Doggy()
    doggy.send_action(DoggyAction.WALK)
    while True:
        t = time.time()
        lx = 0
        ly = 0
        rx = math.sin(t) * 0.1
        ry = 0
        doggy.send_stick(lx, ly, rx, ry)
        time.sleep(0.01)
