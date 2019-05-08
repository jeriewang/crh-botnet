from crh_botnet import *
from gpiozero import LED

# This program works if and only if 2 robots are connected

robot = Robot()
robot.network.set_server_address('choate-robotics-rpi-01.local')

led = LED(17)


def setup():
    robot.network.broadcast("next")


async def on_message(message):
    led.on()
    await sleep(0.5)
    await robot.network.coro.broadcast('next')
    led.off()


robot.run(globals())
