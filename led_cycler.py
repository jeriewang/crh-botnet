from crh_botnet import *


robot=Robot(0)
c=0
async def on_message(message:Message):
    global c
    print(message,c)
    await sleep(0.1)
    await robot.network.coro.broadcast('next')

    c+=1

def setup():
    robot.network.broadcast('Hi')

robot.run(globals())
