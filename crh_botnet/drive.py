class HBridgeDrive:
    
    def __init__(self, left_ground, left_power, left_enable, right_ground, right_power, right_enable, reverse_left=False, reverse_right=False):
        """
        All pin numbers here are GPIO number, not the actual pin number.
        
        :param int left_ground: The GND pin for the left motor
        :param int left_power:  The VCC pin for the left motor
        :param int left_enable: The EN pin for the left motor
        :param int right_ground: The GND pin for the right motor
        :param int right_power: The VCC pin for the right motor
        :param int right_enable: The EN pin for the right motor
        :param bool reverse_left: Reverse the direction of left motor
        :param bool reverse_right: Reverse the direction of right motor
        """
        from gpiozero import PWMOutputDevice, DigitalOutputDevice
        # import  inside the function so devices without GPIO pins won't have error when importing everything
        
        if reverse_left:
            self.left_power = DigitalOutputDevice(left_ground)
            self.left_ground = DigitalOutputDevice(left_power)
        else:
            self.left_ground = DigitalOutputDevice(left_ground)
            self.left_power = DigitalOutputDevice(left_power)
            
        self.left_enable = PWMOutputDevice(left_enable)
        
        if reverse_right:
            self.right_power = DigitalOutputDevice(right_ground)
            self.right_ground = DigitalOutputDevice(right_power)
        else:
            self.right_ground = DigitalOutputDevice(right_ground)
            self.right_power = DigitalOutputDevice(right_power)
        self.right_enable = PWMOutputDevice(right_enable)
    
    def drive(self, power_left, power_right):
        """
        Power left and power right to the motor.
        
        :param float power_left: Power to the left motor, in range [-1,1]
        :param float power_right: Power to the right motor, in range [-1,1]
        :return: None
        """
        
        assert -1 <= power_left <= 1
        assert -1 <= power_right <= 1
        
        if power_left == 0:
            self.left_power.off()
            self.left_ground.off()
        elif power_left > 0:
            self.left_power.on()
            self.left_ground.off()
        else:
            self.left_ground.on()
            self.left_power.off()
        
        if power_right == 0:
            self.right_power.off()
            self.right_ground.off()
        elif power_right > 0:
            self.right_power.on()
            self.right_ground.off()
        else:
            self.right_ground.on()
            self.right_power.off()
        
        self.left_enable.value = abs(power_left)
        self.right_enable.value = abs(power_right)
    
    def stop(self):
        self.left_enable.value = 0
        self.right_enable.value = 0
        self.left_power.off()
        self.left_ground.off()
        self.right_power.off()
        self.right_ground.off()
