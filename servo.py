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
                        [18, 550],
                        [36, 750],
                        [54, 960],
                        [72, 1100],
                        [90, 1310],
                        [108, 1510],
                        [126, 1680],
                        [144, 1900]]
        """
        [45, 1000],
        [90, 1500],
        [135, 2000]]
        """

        np_angle_list = np.array(angle_list)
        pulsewidth_list = np_angle_list[:,1]

        for i in range(len(angle_list)-1):
            smaller_angle = angle_list[i][0]
            smaller_angle_pw = angle_list[i][1]
            larger_angle = angle_list[i+1][0]
            larger_angle_pw = angle_list[i+1][1]
            angle_diff = larger_angle - smaller_angle
            pw_diff_per_deg = (larger_angle_pw - smaller_angle_pw) / angle_diff
            
            for j in range(angle_diff):
                self._full_angle_list.append([smaller_angle + j, int(smaller_angle_pw + pw_diff_per_deg * j)])
                

        # construct full angle list
        #for angle in range(136):
        #    self._full_angle_list.append([angle, int(angles_to_pw(angle))])

        #self._full_angle_list[0] = [0, 510]
        #self._full_angle_list[1] = [1, 510]
        #self._full_angle_list[2] = [2, 510]
        #print(self._full_angle_list)

    def _setAngleSetup(self):
        self._rpi.set_PWM_frequency(self._PWM_PIN, 50) # 50Hz
        self._rpi.set_servo_pulsewidth(self._PWM_PIN, 0)
        
    
    def setAngle(self,angle, sleep_time = 0.05):
        assert(angle <= 144 and angle >= 0)
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
        
        for angle in range(self._current_angle, -1, -1):
            self.setAngle(angle)

    def __del__(self):
        self._reset_position()

