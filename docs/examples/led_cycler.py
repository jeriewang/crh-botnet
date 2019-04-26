from crh_botnet import *
from gpiozero import LED

robot = Robot()
robot.network.set_server_address('choate-robotics-rpi-01.local:5003')

led = LED(17)


def setup():
    robot.network.broadcast("Hi")


async def on_message(message):
    connected_robots = sorted(robot.network.connected_robots)
    
    if message.content == 'next':
        led.on()
        await sleep(0.5)
        connected_robots = sorted(robot.network.connected_robots)
        # re-fetch because connected robots may change over the 0.5 seconds
        
        loc = connected_robots.index(robot.id)
        if loc == len(connected_robots) - 1:
            recipient = connected_robots[0]
        else:
            recipient = connected_robots[loc + 1]
        await robot.network.coro.send('next', recipient)
        led.off()
    elif message.content == 'Hi':
        if len(connected_robots) == 2:
            robot.network.send('next', connected_robots[0])
            # It doesn't matter which robot gets the message, as long as one
            # of the robot starts the chain, so the first one on the list is used.


robot.run(globals())
