from time import sleep
import pigpio
import numpy as np


class ServoMotor:
    def __init__(self):
        self._PWM_PIN = 12
        self._full_angle_list = []
        self._current_pulse_width = 0
        self._current_angle = 0
        self._create_full_angle_list()
        self._rpi = pigpio.pi()
        self._setAngleSetup()

    def _create_full_angle_list(self):
        angle_list = [  [0, 510],
                        [45, 800],
                        [90, 1300],
                        [135, 1850]]

        np_angle_list = np.array(angle_list)

        angles_to_pw = np.poly1d(
            np.polyfit(
                np_angle_list[:, 0],
                np_angle_list[:, 1],
                3
            )
        )

        # construct full angle list
        for angle in range(136):
            self._full_angle_list.append([angle, int(angles_to_pw(angle))])

    def _setAngleSetup(self):
        self._rpi.set_PWM_frequency(self._PWM_PIN, 50) # 50Hz
        self._rpi.set_servo_pulsewidth(self._PWM_PIN, 0)
        
    
    def setAngle(self,angle, sleep_time = 0.02):
        assert(angle <= 135 and angle >= 0)
        angle = int(angle)
        pulse_width = self._full_angle_list[angle][1]
        
        if (pulse_width != self._current_pulse_width):
            self._rpi.set_servo_pulsewidth(self._PWM_PIN, pulse_width)
            sleep(sleep_time)
            self._rpi.set_servo_pulsewidth(self._PWM_PIN, 0)
            self._current_pulse_width = pulse_width
            self._current_angle = angle
        #else:
        #    print("No angle movement needed")


    def _reset_position(self):
        #reseting position to an angle zero
        for angle in range(self._current_angle, 0):
            self.setAngle(angle)

    def __del__(self):
        self._reset_position()

