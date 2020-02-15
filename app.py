# coding=utf-8

from time import sleep
import math
import numpy
import json

try:
    import pigpio
    force_virtual_mode = False
except ModuleNotFoundError:
    print("pigpio not installed, running in test mode")
    force_virtual_mode = True

#import tqdm


class BrachioGraph:

    def __init__(
        self,
        inner_arm,                  # the lengths of the arms
        outer_arm,
        virtual_mode = False,
        wait=None,
        bounds=None,                # the maximum rectangular drawing area
        servo_1_angle_pws=[],       # pulse-widths for various angles
        servo_2_angle_pws=[],
        servo_1_centre=1500,
        servo_2_centre=1500,
        servo_1_degree_ms=-10,      # milliseconds pulse-width per degree
        servo_2_degree_ms=10,       # reversed for the mounting of the elbow servo
        arm_1_centre=-60,
        arm_2_centre=90,
        hysteresis_correction_1=0,  # hardware error compensation
        hysteresis_correction_2=0,
        pw_up=1500,                 # pulse-widths for pen up/down
        pw_down=1100,
    ):

        # set the pantograph geometry
        self.INNER_ARM = inner_arm
        self.OUTER_ARM = outer_arm

        self.virtual_mode = virtual_mode or force_virtual_mode

        #ja sam dodao ovo
        self.angles_used_1 = []
        self.angles_used_2 = []
        pulse_widths_used_1 = []
        pulse_widths_used_2 = []


        # the box bounds describe a rectangle that we can safely draw in
        self.bounds = bounds

        # if pulse-widths to angles are supplied for each servo, we will feed them to
        # numpy.polyfit(), to produce a function for each one. Otherwise, we will use a simple
        # approximation based on a centre of travel of 1500µS and 10µS per degree

        self.servo_1_centre = servo_1_centre
        self.servo_1_degree_ms = servo_1_degree_ms
        self.arm_1_centre = arm_1_centre
        self.hysteresis_correction_1 = hysteresis_correction_1

        self.servo_2_centre = servo_2_centre
        self.servo_2_degree_ms = servo_2_degree_ms
        self.arm_2_centre = arm_2_centre
        self.hysteresis_correction_2 = hysteresis_correction_2

        if servo_1_angle_pws:
            servo_1_array = numpy.array(servo_1_angle_pws)
            self.angles_to_pw_1 = numpy.poly1d(
                numpy.polyfit(
                    servo_1_array[:,0],
                    servo_1_array[:,1],
                    3
                )
            )

        else:
            self.angles_to_pw_1 = self.naive_angles_to_pulse_widths_1

        if servo_2_angle_pws:
            servo_2_array = numpy.array(servo_2_angle_pws)
            self.angles_to_pw_2 = numpy.poly1d(
                numpy.polyfit(
                    servo_2_array[:,0],
                    servo_2_array[:,1],
                    3
                )
            )

        else:
            self.angles_to_pw_2 = self.naive_angles_to_pulse_widths_2


        # create the pen object, and make sure the pen is up
        self.pen = Pen(bg=self, pw_up=pw_up, pw_down=pw_down, virtual_mode=self.virtual_mode)

        if self.virtual_mode:

            print("Initialising virtual BrachioGraph")

            self.virtual_pw_1 = self.angles_to_pw_1(-90)
            self.virtual_pw_2 = self.angles_to_pw_2(90)

            # by default in virtual mode, we use a wait factor of 0 for speed
            self.wait = wait or 0

            print("    Pen is up")
            print("    Pulse-width 1", self.virtual_pw_1)
            print("    Pulse-width 2", self.virtual_pw_2)

        else:

            # instantiate this Raspberry Pi as a pigpio.pi() instance
            self.rpi = pigpio.pi()

            # the pulse frequency should be no higher than 100Hz - higher values could (supposedly) damage the servos
            self.rpi.set_PWM_frequency(14, 50)
            self.rpi.set_PWM_frequency(15, 50)

            # Initialise the pantograph with the motors in the centre of their travel
            self.rpi.set_servo_pulsewidth(14, self.angles_to_pw_1(-90))
            sleep(0.3)
            self.rpi.set_servo_pulsewidth(15, self.angles_to_pw_2(90))
            sleep(0.3)

            # by default we use a wait factor of 0.1 for accuracy
            self.wait = wait or .1

        # Now the plotter is in a safe physical state.

        # Set the x and y position state, so it knows its current x/y position.
        self.current_x = -self.INNER_ARM
        self.current_y = self.OUTER_ARM


        self.previous_pw_1 = self.previous_pw_2 = 0
        self.active_hysteresis_correction_1 = self.active_hysteresis_correction_2 = 0

    # methods in this class:
    # drawing
    # line-processing
    # test patterns
    # pen-moving methods
    # angles-to-pulse-widths
    # hardware-related
    # trigonometric methods
    # calibration
    # manual driving methods
    # reporting methods

    # ----------------- drawing methods -----------------






    def draw_line(self, start=(0, 0), end=(0, 0), wait=0, interpolate=10, both=False):

        wait = wait or self.wait

        start_x, start_y = start
        end_x, end_y = end

        self.pen.up()
        self.xy(x=start_x, y=start_y, wait=wait, interpolate=interpolate)

        self.pen.down()
        self.draw(x=end_x, y=end_y, wait=wait, interpolate=interpolate)

        if both:
            self.draw(x=start_x, y=start_y, wait=wait, interpolate=interpolate)

        self.pen.up()


    def draw(self, x=0, y=0, wait=0, interpolate=10):

        wait = wait or self.wait

        self.xy(x=x, y=y, wait=wait, interpolate=interpolate, draw=True)

    # ----------------- line-processing methods -----------------



    # ----------------- test pattern methods -----------------


    def vertical_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        if not reverse:
            top_y =    self.bounds[1]
            bottom_y = self.bounds[3]
        else:
            bottom_y = self.bounds[1]
            top_y =    self.bounds[3]

        step = (self.bounds[2] - self.bounds[0]) /  lines
        x = self.bounds[0]
        while x <= self.bounds[2]:
            self.draw_line((x, top_y), (x, bottom_y), interpolate=interpolate, both=both)
            x = x + step

        self.park()


    def horizontal_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        if not reverse:
            min_x = self.bounds[0]
            max_x = self.bounds[2]
        else:
            max_x = self.bounds[0]
            min_x = self.bounds[2]

        step = (self.bounds[3] - self.bounds[1]) / lines
        y = self.bounds[1]
        while y <= self.bounds[3]:
            self.draw_line((min_x, y), (max_x, y), interpolate=interpolate, both=both)
            y = y + step

        self.park()


    def grid_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

        self.vertical_lines(
            bounds=bounds, lines=lines, wait=wait, interpolate=interpolate, repeat=repeat, reverse=reverse, both=both
            )
        self.horizontal_lines(
            bounds=bounds, lines=lines, wait=wait, interpolate=interpolate, repeat=repeat, reverse=reverse, both=both
            )



    # ----------------- pen-moving methods -----------------

    def xy(self, x=0, y=0, wait=0, interpolate=10, draw=False):
        # Moves the pen to the xy position; optionally draws

        wait = wait or self.wait

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        (angle_1, angle_2) = self.xy_to_angles(x, y)
        (pulse_width_1, pulse_width_2) = self.angles_to_pulse_widths(angle_1, angle_2)

        # if they are the same, we don't need to move anything
        if (pulse_width_1, pulse_width_2) == self.get_pulse_widths():

            # ensure the pantograph knows its x/y positions
            self.current_x = x
            self.current_y = y

            return


        # calculate how many steps we need for this move, and the x/y length of each
        (x_length, y_length) = (x - self.current_x, y - self.current_y)

        length = math.sqrt(x_length ** 2 + y_length **2)

        no_of_steps = int(length * interpolate) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_x, length_of_step_y) = (x_length/no_of_steps, y_length/no_of_steps)

        #ja sam izmenio umesto tqdm.tqdm
        for step in range(no_of_steps):

            self.current_x = self.current_x + length_of_step_x
            self.current_y = self.current_y + length_of_step_y

            angle_1, angle_2 = self.xy_to_angles(self.current_x, self.current_y)

            self.set_angles(angle_1, angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait/no_of_steps)

        sleep(length * wait/10)


    def set_angles(self, angle_1=0, angle_2=0):
        # moves the servo motor

        pw_1, pw_2 = self.angles_to_pulse_widths(angle_1, angle_2)

        if pw_1 > self.previous_pw_1:
            self.active_hysteresis_correction_1 = self.hysteresis_correction_1
        elif pw_1 < self.previous_pw_1:
            self.active_hysteresis_correction_1 = - self.hysteresis_correction_1

        if pw_2 > self.previous_pw_2:
            self.active_hysteresis_correction_2 = self.hysteresis_correction_2
        elif pw_2 < self.previous_pw_2:
            self.active_hysteresis_correction_2 = - self.hysteresis_correction_2

        self.previous_pw_1 = pw_1
        self.previous_pw_2 = pw_2

        self.set_pulse_widths(pw_1 + self.active_hysteresis_correction_1, pw_2 + self.active_hysteresis_correction_2)

        # We record the angles, so we that we know where the arms are for future reference.
        self.angle_1, self.angle_2 = angle_1, angle_2

        self.angles_used_1.append(int(angle_1))
        self.angles_used_2.append(int(angle_2))
        self.pulse_widths_used_1.append(int(pw_1))
        self.pulse_widths_used_2.append(int(pw_2))




    #  ----------------- angles-to-pulse-widths methods -----------------
    def naive_angles_to_pulse_widths_1(self, angle):
        return (angle - self.arm_1_centre) * self.servo_1_degree_ms + self.servo_1_centre

    def naive_angles_to_pulse_widths_2(self, angle):
        return (angle - self.arm_2_centre) * self.servo_2_degree_ms + self.servo_2_centre


    def angles_to_pulse_widths(self, angle_1, angle_2):
        # Given a pair of angles, returns the appropriate pulse widths.

        # at present we assume only one method of calculating, using the angles_to_pw_1 and angles_to_pw_2
        # functions created using numpy

        pulse_width_1, pulse_width_2 = self.angles_to_pw_1(angle_1), self.angles_to_pw_2(angle_2)

        return (pulse_width_1, pulse_width_2)


    #  ----------------- hardware-related methods -----------------

    def set_pulse_widths(self, pw_1, pw_2):

        if self.virtual_mode:

            if (500 < pw_1 < 2500) and (500 < pw_2 < 2500):

                self.virtual_pw_1 = self.angles_to_pw_1(pw_1)
                self.virtual_pw_2 = self.angles_to_pw_2(pw_2)

            else:
               raise ValueError

        else:

            self.rpi.set_servo_pulsewidth(14, pw_1)
            self.rpi.set_servo_pulsewidth(15, pw_2)


    def get_pulse_widths(self):

        if self.virtual_mode:

            actual_pulse_width_1 = self.virtual_pw_1
            actual_pulse_width_2 = self.virtual_pw_2

        else:

            actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
            actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return (actual_pulse_width_1, actual_pulse_width_2)


    def park(self):

        # parks the plotter

        if self.virtual_mode:
            print("Parking")

        self.pen.up()
        self.xy(-self.INNER_ARM, self.OUTER_ARM)
        sleep(1)
        # self.quiet()



    # ----------------- trigonometric methods -----------------

    # Every x/y position of the plotter corresponds to a pair of angles of the arms. These methods
    # calculate:
    #
    # the angles required to reach any x/y position
    # the x/y position represented by any pair of angles

    def xy_to_angles(self, x=0, y=0):

        # convert x/y co-ordinates into motor angles

        hypotenuse = math.sqrt(x**2+y**2)

        if hypotenuse > self.INNER_ARM + self.OUTER_ARM:
            raise Exception(f"Cannot reach {hypotenuse}; total arm length is {self.INNER_ARM + self.OUTER_ARM}")

        hypotenuse_angle = math.asin(x/hypotenuse)

        inner_angle = math.acos(
            (hypotenuse**2+self.INNER_ARM**2-self.OUTER_ARM**2)/(2*hypotenuse*self.INNER_ARM)
        )
        outer_angle = math.acos(
            (self.INNER_ARM**2+self.OUTER_ARM**2-hypotenuse**2)/(2*self.INNER_ARM*self.OUTER_ARM)
        )

        shoulder_motor_angle = hypotenuse_angle - inner_angle
        elbow_motor_angle = math.pi - outer_angle

        return (math.degrees(shoulder_motor_angle), math.degrees(elbow_motor_angle))




    # ----------------- calibration -----------------


    # ----------------- manual driving methods -----------------


    @property
    def bl(self):
        return (self.bounds[0], self.bounds[1])

    @property
    def tl(self):
        return (self.bounds[0], self.bounds[3])

    @property
    def tr(self):
        return (self.bounds[2], self.bounds[3])

    @property
    def br(self):
        return (self.bounds[2], self.bounds[1])


class Pen:

    def __init__(self, bg, pw_up=1700, pw_down=1300, pin=18, transition_time=0.25, virtual_mode=False):

        self.bg = bg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time
        self.virtual_mode = virtual_mode
        if self.virtual_mode:

            print("Initialising virtual Pen")

        else:

            self.rpi = pigpio.pi()
            self.rpi.set_PWM_frequency(self.pin, 50)

        self.up()
        sleep(0.3)
        self.down()
        sleep(0.3)
        self.up()
        sleep(0.3)


    def down(self):

        if self.virtual_mode:
            self.virtual_pw = self.pw_down

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_down)
            sleep(self.transition_time)


    def up(self):

        if self.virtual_mode:
            self.virtual_pw = self.pw_up

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_up)
            sleep(self.transition_time)


    # for convenience, a quick way to set pen motor pulse-widths
    def pw(self, pulse_width):

        if self.virtual_mode:
            self.virtual_pw = pulse_width

        else:
            self.rpi.set_servo_pulsewidth(self.pin, pulse_width)


if __name__ == '__main__':
    # A "naively" calibrated plotter definition. We assume the default 10ms
    # pulse-width difference = 1 degree of motor movement. If the arms appear to
    # move in the wrong directions, try reversing the value of servo_1_degree_ms
    # and/or servo_2_degree_ms.

    naive_bg = BrachioGraph(
        # the lengths of the arms
        inner_arm=8,
        outer_arm=8,
        # the drawing area
        bounds=(-6, 4, 6, 12),
        # relationship between servo angles and pulse-widths
        servo_1_degree_ms=-10,
        servo_2_degree_ms=10,
        # pulse-widths for pen up/down
        pw_down=1200,
        pw_up=1850,
    )
    naive_bg.draw_line(start=(1,1), end=(1,3))