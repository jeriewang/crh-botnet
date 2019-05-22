from crh_botnet import *

robot = Robot()
robot.network.set_server_address('choate-robotics-rpi-01.local')


def on_message(message: Message):
    print("Robot", message.sender, "said", message.content)
    
    if message.content == 'Hi':  # avoid infinite looping
        robot.network.send('Hi to you too', message.sender)

def setup():
    robot.network.broadcast('Hi')


robot.run(globals())
