from crh_botnet import *
import datetime, time

robot = Robot(0)

def setup():
    c = 0

def on_shutdown():
    print('The robot is shutting down')


def on_message(message):
    print(message)


def loop():
    global c, start
    if c == 0:
        start = time.time()
    c += 1
    #await sleep(10)
    if time.time() - start >= 1:
        print(c)
        raise Exception


robot.run(globals())
print('This line is never reached')
