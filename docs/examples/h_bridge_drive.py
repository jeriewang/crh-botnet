from crh_botnet import *
from crh_botnet.drive import HBridgeDrive

robot = Robot()
driver = HBridgeDrive(20, 26, 18, 22, 23, 17, reverse_left=True)


def loop():
    driver.drive(1, 1)


robot.run(globals(), offline=True, debug=True)
