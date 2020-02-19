import RPi.GPIO as GPIO
from time import sleep

class StepperMotor:
    
    def __init__(self):
        self.pin1,self.pin2,self.pin3,self.pin4 =  (5,7,31,29)        
        self.current_angle = 0
        self._ONE_STEPPER_ANGLE = 360/400 # full circle divided by number of steps that stepper can made in a full circle
        self._substep_forwards = 0
        self._substep_backwards = 0
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)
        GPIO.setup(self.pin3, GPIO.OUT)
        GPIO.setup(self.pin4, GPIO.OUT)

    def forward_step(self):
        if self._substep_forwards == 0:
            self.set_stepper(1,0,1,0)
            self._substep_forwards += 1
        elif self._substep_forwards == 1:
            self.set_stepper(0,1,1,0)
            self._substep_forwards += 1
        elif self._substep_forwards == 2:
            self.set_stepper(0,1,0,1)
            self._substep_forwards += 1
        else:
            self.set_stepper(1,0,0,1)
            self._substep_forwards = 0
        
    def backward_step(self):
        if self._substep_backwards == 0:
            self.set_stepper(1,0,0,1)
            self._substep_backwards += 1
        elif self._substep_backwards == 1:
            self.set_stepper(0,1,0,1)
            self._substep_backwards += 1
        elif self._substep_backwards == 2:
            self.set_stepper(0,1,1,0)
            self._substep_backwards += 1
        else:
            self.set_stepper(1,0,1,0)
            self._substep_backwards = 0
        

    def set_stepper(self,in1,in2,in3,in4):
        GPIO.output(self.pin1, in1)
        GPIO.output(self.pin2, in2)
        GPIO.output(self.pin3, in3)
        GPIO.output(self.pin4, in4)
        sleep(0.02)

    def transform_angle_to_steps(self,angle= 0):
        steps = int(angle * 400 /360) # it is the same as ( angle / self._ONE_STEPPER_ANGLE )
        return steps

    def setAngle(self,angle):
        #new_angle = self.current_angle + angle
        #print("angle is %d" % angle)
        #print("new_angle is %d" % new_angle)
        assert(angle < 90 and angle > -110)
               
        angle_to_move = angle - self.current_angle
        if(angle_to_move >= 0):      
            steps = self.transform_angle_to_steps(angle_to_move)
            #print(steps)
            for step in range(steps):
                self.backward_step()
                self.current_angle += self._ONE_STEPPER_ANGLE
        else:
            angle_to_move = abs(angle_to_move)
            steps = self.transform_angle_to_steps(angle_to_move)
            for step in range(steps):
                self.forward_step()
                self.current_angle -= self._ONE_STEPPER_ANGLE


    # this method is never called. This an example of what should one movement represent
    def move(self, angle):
        self._setup()
        self.setAngle(angle)
        GPIO.cleanup()

    def _reset_position(self):
        self._setup()
        self.setAngle(0)
        GPIO.cleanup()
    
    def __del__(self):
        self._reset_position()
        
        # Hack to stop cleanup from turning off the internal pull ups
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
