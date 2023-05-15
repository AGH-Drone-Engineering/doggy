import paho.mqtt.client as mqtt
import struct
import time
from enum import Enum
import math
import asyncio


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
        self.is_connected = False

        self.client = mqtt.Client("Doggy")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        self.client.loop_start()

    def wait_connected(self):
        while not self.is_connected:
            time.sleep(0.05)

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
        self.is_connected = True

    def on_message(self, client, userdata, msg):
        if msg.topic == "controller/stick":
            lx, rx, ry, ly = struct.unpack('ffff', msg.payload)
            print(f"Stick = ({lx} {ly}) ({rx} {ry})")


if __name__ == "__main__":
    doggy = Doggy()
    doggy.wait_connected()
    doggy.send_action(DoggyAction.WALK)
    counter=0
    try:
        while True and counter<10:
            counter+=1

            t = time.time()
            lx = 0 #chodzenie w prawo jak na plusie
            ly = 0.1 #chodzenie przód, tył
            rx = (90-(180-math.pi/36)/2)*math.pi/180 #math.sin(t) * 0.1 #obrót względem osi z, jak na plsuie to głowa idzie w prawo
            if rx >= 0.3:
                rx = 0
            ry = 0
            doggy.send_stick(lx, ly, rx, ry)
            time.sleep(0.1)
    except KeyboardInterrupt:
        for _ in range(10):
            time.sleep(0.1)
            doggy.send_stick(0, 0, 0, 0)
