try:
    import RPi.GPIO as GPIO
    from time import sleep

    class ServoMotor:
        def __init__(self):
            self.pwm = None #setting the value in move() method

        def setAngle(self,angle):
            duty = angle / 18 + 2
            GPIO.output(3, True)  # turn on the pin for output
            self.pwm.ChangeDutyCycle(duty)  # changes duty cycle to match the calculation
            sleep(0.5)  # waiting 1 sec so the servo has time to make the turn
            GPIO.output(3, False)  # turn off the pin
            self.pwm.ChangeDutyCycle(0)  # stop sending inputs to the servo
            print(duty)

        def move(self,angle):
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(3, GPIO.OUT) #pin 3 is gpio out
            self.pwm = GPIO.PWM(3,50) #setting pwm to 50Hz
            self.pwm.start(0) #doesn't set any angles on startup

            self.setAngle(angle=angle)
            self.pwm.stop()
            GPIO.cleanup()

        def reset_position(self):
            self.move(0)


    class StepperMotor:
        
        def __init__(self):
            self.pin1,self.pin2,self.pin3,self.pin4 = (5,7,31,29)
            self.current_angle = 0

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

        def set_stepper(self, in1,in2,in3,in4):
            GPIO.output(self.pin1, in1)
            GPIO.output(self.pin2, in2)
            GPIO.output(self.pin3, in3)
            GPIO.output(self.pin4, in4)
            sleep(0.01)

        def transform_angle_to_steps(self,angle=0):
            steps = angle * 50 / 360
            steps= int(steps)
            return steps

        def setAngle(self,angle):
            angle_to_move = angle - self.current_angle
            if(angle_to_move >=0):
                steps = self.transform_angle_to_steps(angle)
                for step in range(steps):
                    self.forward_step()

            else:
                angle_to_move = abs(angle_to_move)
                steps = self.transform_angle_to_steps(angle_to_move)
                for step in range(steps):
                    self.backward_step()

            self.current_angle = angle

        def move(self,angle):
            self.setup()
            self.setAngle(angle)
            GPIO.cleanup()


        def reset_position(self):
            self.move(0)


except ImportError:
    print('this is not running on rpi3')





if __name__ == '__main__':
    stepper = StepperMotor()
    stepper.move(90)
    stepper.move(0)
    stepper.reset_position()