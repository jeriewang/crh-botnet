from crh_botnet import *
robot=Robot()

def on_message(message:Message):
    if message.content=='Hi': # avoid infinite looping
        robot.network.send('Hi to you too',message.sender)

def setup():
    robot.network.broadcast('Hi')

robot.run(globals())
