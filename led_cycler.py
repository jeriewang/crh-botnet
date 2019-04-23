from crh_botnet import *
import gpiozero

robot=Robot()

async def on_message(message:Message):
    
    connected_bots=await robot.network.coro.get_connected_robots()
    
    await robot.network.coro.broadcast('next')
    

robot.run(globals())
