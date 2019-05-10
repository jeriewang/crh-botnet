from crh_botnet import *
import gpiozero

robot = Robot()
robot.network.set_server_address('choate-robotics-rpi-01.local')

motor_left = gpiozero.PWMOutputDevice(17)
motor_right = gpiozero.PWMOutputDevice(18)

H_left_1 = gpiozero.DigitalOutputDevice(22)
H_left_2 = gpiozero.DigitalOutputDevice(23)

H_right_1 = gpiozero.DigitalOutputDevice(26)
H_right_2 = gpiozero.DigitalOutputDevice(20)


def setup():
    H_left_1.on()
    H_right_1.on()


def on_message(message):
    if message == 'on':
        motor_left.value = 0.75
        motor_right.value = 0.75
    elif message == 'off':
        motor_left.value = 0
        motor_right.value = 0


robot.run(globals())
