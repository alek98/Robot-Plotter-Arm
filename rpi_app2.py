import math
from boundaries import Boundaries
from photos import Photo
from time import sleep
try:
    from servo import ServoMotor
    from stepper import StepperMotor
    mode = 'normal'
except ImportError:
    print('cannot import servo and stepper motor classes. \n Running virtual mode... ')
    from virtual_servo import ServoMotor
    from virtual_stepper import StepperMotor


    mode = 'virtual'
    global plot_counter
    plot_counter = 0

# =========hardware functions===========
# ======================================

def set_inner_angle(inner_angle):
    stepper.setAngle(inner_angle)

    # ========plotting graphic======
    #==============================
    if (mode == 'virtual' and 'pen' in globals()):
        global plot_counter
        if (plot_counter <= 5):
            plot_counter += 1
        else:
            plot_counter = 0
            stepper.plot(inner_angle, pen)


def set_outer_angle(outer_angle):
    servo.setAngle(outer_angle)



# ===========software functions==========
# =======================================

def set_angles(inner_angle, outer_angle):

    set_inner_angle(inner_angle)
    set_outer_angle(outer_angle)

def convert_xy_to_angles(x, y):
    try:
        inner_angle = outer_angle = 0
        hypotenuse = math.sqrt(x **2 + y ** 2)
        beta = math.asin(x / hypotenuse)
        delta = math.acos((hypotenuse ** 2 + pen.inner_arm** 2 - pen.outer_arm ** 2) / (2 * hypotenuse * pen.inner_arm))
        inner_angle = beta - delta

        gamma = math.acos((pen.inner_arm ** 2 + pen.outer_arm ** 2 - hypotenuse ** 2) / (2 * pen.inner_arm * pen.outer_arm))

        outer_angle = math.pi - gamma

        #now convert radians to degrees
        inner_angle = math.degrees(inner_angle)
        outer_angle = math.degrees(outer_angle)

        return inner_angle, outer_angle

    except ValueError:
        msg = '(' + str(x) + ' , ' + str(y) + ')' + ' coordinates are not reachable with inner and outer arms'
        raise ValueError(msg)


def calculations(start = (0,0), end = (0,0)):
    #calculates length_of_step_x, length_of_step_y, number_of_steps
    #these values are used in draw_line function
    #start calculations
    start_x, start_y = start
    end_x, end_y = end
    length_x = end_x - start_x
    length_y = end_y - start_y

    length = math.sqrt(length_x ** 2 + length_y ** 2) #total line length

    number_of_steps = int(length * 20)
    if number_of_steps == 0:
        length_of_step_x = length_of_step_y = 0
    else:
        length_of_step_x = length_x / number_of_steps
        length_of_step_y = length_y / number_of_steps
    


    return length_of_step_x, length_of_step_y, number_of_steps


def draw_line(start = (0,0), end = (0,0)):
    #first of all, check if it's possible to draw a line = check drawable area = check boundaries
    line_is_drawable = boundaries.check_boundaries(start, end)
    if line_is_drawable is False:
        return 'this line is not drawable'

    pen.park(start=start) # move pen so that it's on the start coordinate

    # actual line drawing
    pen.move_pen(start, end)


def draw_photo1(photo):
    # this function draws more precise
    lines = photo.get_lines()
    for line in lines:
        start_dot = end_dot = line[0]
        index = 0
        for dot in line:
            end_dot = dot

            if index == 0:
                index += 1
                continue

            draw_line(start=start_dot, end=end_dot)
            start_dot = end_dot


def draw_photo2(photo):

    lines = photo.get_lines()
    max_line_length = 0
    for line in lines:
        max_line_length = max(max_line_length, len(line))
        start_dot = line[0]
        end_dot = line[-1]
        draw_line(start=start_dot, end=end_dot)


class Pen:
    def __init__(self):
        self._x = 0
        self._y = 16.2
        self._inner_angle = 0
        self._outer_angle = 0
        self.inner_arm = 8
        self.outer_arm = 8.2
        set_angles(self._inner_angle, self._outer_angle)


    def get_current_position(self):
        return (self._x, self._y)
    def set_current_position(self, x, y):
        self._x = x
        self._y = y

    def get_current_angles(self):
        return (self._inner_angle, self._outer_angle)
    def set_current_angles(self, inner_angle, outer_angle):
        self._inner_angle = inner_angle
        self._outer_angle = outer_angle

    def _update_positions_and_angles(self, x, y, inner_angle, outer_angle):
        self.set_current_position(x, y)
        self.set_current_angles(inner_angle, outer_angle)


    def park(self,start):
        # initializes the starting position of pen. moves pen to start coordinates
        # start coordinate is should be initial position of pen
        # we should park our pen at start coordinate.
        # therefore start coordinate is our stop. starting position is our current coordinate
        end = start
        start = (self._x, self._y)

        self.move_pen(start, end)



    def move_pen(self, start, end):
        pen_x, pen_y = pen.get_current_position()

        # calculate length_of_step_x, length_of_step_y, number_of_steps
        # this calculation is in separate function just to make code cleaner
        length_of_step_x, length_of_step_y, number_of_steps = calculations(start, end)

        # actual line drawing
        for step in range(number_of_steps):
            pen_x += length_of_step_x
            pen_y += length_of_step_y

            pen._move_pen_to_xy(pen_x, pen_y)


    # moving pen to new xy position
    def _move_pen_to_xy(self, x=0.0, y=0.0):
        inner_angle, outer_angle = convert_xy_to_angles(x, y)

        # set_angles function will call hardware functions for moving motors to a specific angle
        set_angles(inner_angle, outer_angle)

        # update current position of a pen and update current angles
        self._update_positions_and_angles(x, y, inner_angle, outer_angle)


def test():
    start = (3, 10)
    end = (3, 6)
    draw_line(start, end)

    start = (3, 8)
    end = (-3, 8)
    draw_line(start, end)

def test2(photo):
    from time import time
    t1 = time()
    draw_photo1(photo)
    t2 = time()
    print('time1: ' , round(t2 - t1, 2))

    t1 = time()
    draw_photo2(photo)
    t2 = time()
    print('time2: ' , round(t2 - t1, 2))

if __name__ == '__main__':
    stepper = StepperMotor()
    servo = ServoMotor()

    boundaries = Boundaries(
        left_down_corner= (-4.7, 5.85),
        right_down_corner = (4.7, 5.85),
        left_up_corner= (-4.7, 15.35),
        right_up_corner=(4.7, 15.35)
    )
    pen = Pen()
    photo = Photo('palm')
    test2(photo)
    sleep(3)
    # explicit deletation is need in order to call destructor.
    # in destructors we reset positions of motors to 0 degrees and clean GPIO
    del stepper
    del servo