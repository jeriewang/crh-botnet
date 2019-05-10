from crh_botnet import *
from gpiozero import Button
from functools import partial

robot = Robot()
robot.network.set_server_address("choate-robotics-rpi-01.local")


def setup():
    button = Button(15)
    button.when_pressed = partial(robot.network.send, 'on', 0)
    button.when_released = partial(robot.network.send, 'off', 0)


robot.run(globals())
