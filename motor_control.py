import numpy as np
import time
import pygame

np.set_printoptions(suppress=True)



########## Joystick ##########
class JoystickControl(object):

    def __init__(self):
        pygame.init()
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()
        self.deadband = 0.1
        self.timeband = 0.5
        self.lastpress = time.time()
        self.gain = 0.1
        self.motor_pos = {"motor1": np.pi/2, 
                          "motor2": np.pi + np.pi/6,
                          "motor3": 2 * np.pi - np.pi/6}

    def getInput(self):
        pygame.event.get()
        curr_time = time.time()
        left_analog_x = self.gamepad.get_axis(1)
        left_analog_y = self.gamepad.get_axis(0)
        right_analog = self.gamepad.get_axis(4)
        left_analog_x = 0.0 if abs(left_analog_x) < self.deadband else left_analog_x
        left_analog_y = 0.0 if abs(left_analog_y) < self.deadband else left_analog_y
        right_analog = 0.0 if abs(right_analog) < self.deadband else right_analog
        A_pressed = self.gamepad.get_button(0) and (curr_time - self.lastpress > self.timeband)
        B_pressed = self.gamepad.get_button(1) and (curr_time - self.lastpress > self.timeband)
        X_pressed = self.gamepad.get_button(2) and (curr_time - self.lastpress > self.timeband)
        Y_pressed = self.gamepad.get_button(3) and (curr_time - self.lastpress > self.timeband)
        START_pressed = self.gamepad.get_button(7) and (curr_time - self.lastpress > self.timeband)
        BACK_pressed = self.gamepad.get_button(6) and (curr_time - self.lastpress > self.timeband)
        pressed_keys = [A_pressed, B_pressed, X_pressed, Y_pressed, START_pressed, left_analog_x, left_analog_y, right_analog]
        if any(pressed_keys):
            self.lastpress = curr_time
        return A_pressed, B_pressed, X_pressed, Y_pressed, (-left_analog_x, left_analog_y, right_analog), BACK_pressed

    
    def motorInput(self, x_vel, y_vel):
        mag = np.sqrt(x_vel ** 2 + y_vel ** 2) * self.gain
        direction = joystick.analogDirection(x_vel, y_vel)
        command = [0.] * 3
        if direction == self.motor_pos["motor1"]:
            command = [mag, 0., 0.]
        elif direction == self.motor_pos["motor2"]:
            command = [0., mag, 0.]
        elif direction == self.motor_pos["motor3"]:
            command = [0., 0., mag]
        elif (self.motor_pos["motor3"] < direction <= 2 * np.pi) or (0 <= direction < self.motor_pos["motor1"]):
            ratio1, ratio3 = self.computeRatio(direction, "motor1", "motor3")
            command = [mag * ratio1, 0., mag * ratio3]
        elif self.motor_pos["motor1"] < direction < self.motor_pos["motor2"]:
            ratio1, ratio2 = self.computeRatio(direction, "motor1", "motor2")
            command = [mag * ratio1, mag * ratio2, 0.]
        elif self.motor_pos["motor2"] < direction < self.motor_pos["motor3"]:
            ratio2, ratio3 = self.computeRatio(direction, "motor2", "motor3")
            command = [0., mag * ratio2, mag * ratio3]
        return command


    def computeRatio(self, direction, motor_a, motor_b):
        motor2motor_dist = 2 * np.pi / 3
        dist2motor_a = abs(direction - self.motor_pos[motor_a])
        dist2motor_b = abs(direction - self.motor_pos[motor_b])
        ## fix wrapping
        dist2motor_a = (2 * np.pi - dist2motor_a) if dist2motor_a > np.pi else dist2motor_a
        dist2motor_b = (2 * np.pi - dist2motor_b) if dist2motor_b > np.pi else dist2motor_b
        ## compute ratios
        ratio_a, ratio_b = 1 - (dist2motor_a / motor2motor_dist), 1 - (dist2motor_b / motor2motor_dist)
        return ratio_a, ratio_b

    def analogDirection(self, x_vel, y_vel):
        angle = np.arctan2(x_vel, y_vel)
        if np.rad2deg(angle) < 0:
            angle += 2 * np.pi
        return angle




## initialize joystick
joystick = JoystickControl()

## parameters	
shutdown = False


while not shutdown:

    ## read joystick commands
    A_pressed, B_pressed, X_pressed, _, analogs, _ = joystick.getInput()
    x_vel, y_vel, _ = analogs
    
    input_motor1, input_motor2, input_motor3 = joystick.motorInput(x_vel, y_vel)

    print("[*] motor1: {}, motor2: {}, motor3: {}\n".format(round(input_motor1, 3), round(input_motor2, 3), round(input_motor3, 3)))