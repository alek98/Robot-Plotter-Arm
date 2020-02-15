import RPi.GPIO as GPIO
from time import sleep

class StepperMotor:
    
    def __init__(self):
        self.pin1,self.pin2,self.pin3,self.pin4 =  (5,7,31,29)        
        self.current_angle = 0
        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)
        GPIO.setup(self.pin3, GPIO.OUT)
        GPIO.setup(self.pin4, GPIO.OUT)

    def forward_step(self):
        self.set_stepper(1,0,1,0)
        self.set_stepper(0,1,1,0)
        self.set_stepper(0,1,0,1)
        self.set_stepper(1,0,0,1)
        
    def backward_step(self):
        self.set_stepper(1,0,0,1)
        self.set_stepper(0,1,0,1)
        self.set_stepper(0,1,1,0)
        self.set_stepper(1,0,1,0)

    def set_stepper(self,in1,in2,in3,in4):
        GPIO.output(self.pin1, in1)
        GPIO.output(self.pin2, in2)
        GPIO.output(self.pin3, in3)
        GPIO.output(self.pin4, in4)
        sleep(0.01)

    def transform_angle_to_steps(self,angle= 0):
        steps = int(angle * 50 /360)
        return steps

    def setAngle(self,angle):
        angle_to_move = angle - self.current_angle
        if(angle_to_move >= 0):      
            steps = self.transform_angle_to_steps(angle_to_move)
            for step in range(steps):
                self.backward_step()
                self.current_angle += 360/50
        else:
            angle_to_move = abs(angle_to_move)
            steps = self.transform_angle_to_steps(angle_to_move)
            for step in range(steps):
                self.forward_step()
                self.current_angle -= 360/50
        
        
        



    def move(self, angle):
        self.setup()
        self.setAngle(angle)
        GPIO.cleanup()

    def _reset_position(self):
        self.setAngle(0)
    
    def __del__(self):
        #self._reset_position()
        GPIO.cleanup()
