import paho.mqtt.client as mqtt
import struct
import time
from enum import Enum
import math
import asyncio
import numpy as np 
from math import atan2

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

class Walk(Doggy):

    def yaw_velocity(self):

        self.send_action(DoggyAction.WALK)

    def recalcuate_geo_to_local(self):
        #TODO
        pass
    @staticmethod
    def walk_forward(self, theta_real: float, goal: list, pose: list):
        # regualtor P do chodzenia w przód oraz zmiana w osi yaw
        theta = 3.14 / 2  # theta is a value is radians

        v = 0.0  # default linear velocity
        w = 0.0  # default angluar velocity
        distance = np.sqrt((pose[0] - goal[0]) ** 2 + (pose[1] - goal[1]) ** 2)
        if (distance > 0.1):
            # v = self.vconst

            desireYaw = atan2(goal[1] - pose[1], goal[0] - pose[0])
            u = desireYaw - theta
            bound = atan2(np.sin(u), np.cos(u))
            w = min(0.5 * 3, max(-0.5, 15 * bound))
            v = min(0.5, distance + 0.2) * 1 if max(-u, u) < 0.52 else 0
        else:
            v, w = 0.0, 0.0

        return v, w


if __name__ == "__main__":
    doggy = Doggy()
    doggy.wait_connected()
    doggy.send_action(DoggyAction.WALK)

    try:


        lx = 0 #chodzenie w prawo jak na plusie
        ly = 0.1 #chodzenie przód, tył
        rx = (90-(180-math.pi/36)/2)*math.pi/180 #math.sin(t) * 0.1 #obrót względem osi z, jak na plsuie to głowa idzie w prawo
        if rx >= 0.3:
            rx = 0
        ry = 0
        doggy.send_stick(lx, ly, rx, ry)
        time.sleep(0.1)
        #obliczenie dystansu pomiędzy punktami







    except KeyboardInterrupt:
        for _ in range(10):
            time.sleep(0.1)
            doggy.send_stick(0, 0, 0, 0)
