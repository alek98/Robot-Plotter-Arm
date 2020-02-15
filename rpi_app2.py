import math
try:
    from servo import ServoMotor
    from stepper import StepperMotor
except ImportError:
    raise ImportError('cannot import servo and stepper motor classes ')


def set_inner_angle(inner_angle):
    try:
        stepper.setAngle()
    except:
        print('inner angle on inner motor is set to: ' + str(inner_angle))
def set_outer_angle(outer_angle):
    try:
        servo.setAngle()
    except:
        print('outer angle on outer motor is set to: ' + str(outer_angle))

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

def set_angles(inner_angle, outer_angle):
    #take into consideration the starting angles
    set_inner_angle(inner_angle)
    set_outer_angle(outer_angle)


def calculations(start = (0,0), end = (0,0)):
    #calculates length_of_step_x, length_of_step_y, number_of_steps
    #these values are used in draw_line function
    #start calculations
    start_x, start_y = start
    end_x, end_y = end
    length_x = start_x - end_x #abs?
    length_y = start_y - end_y #abs?

    length = math.sqrt(length_x ** 2 + length_y ** 2) #total line length

    number_of_steps = int(length * 100)

    length_of_step_x = length_x / number_of_steps
    length_of_step_y = length_y / number_of_steps

    return length_of_step_x, length_of_step_y, number_of_steps




def draw_line(start = (0,0), end = (0,0)):
    #first of all, check if it's possible to draw a line = check drawable area = check boundaries
    line_is_drawable = boundaries.check_boundaries(start, end)
    if line_is_drawable is False:
        return ('this line is not drawable')


    #calculate length_of_step_x, length_of_step_y, number_of_steps
    #this calculation is in separate function just to make code cleaner
    length_of_step_x, length_of_step_y, number_of_steps = calculations(start,end)


    pen.park(start=start) #move pen so that it's on the start coordinate

    pen_x, pen_y = pen.get_current_position()

    #actual line drawing
    for step in range(number_of_steps):
        pen_x += length_of_step_x
        pen_y += length_of_step_y

        pen.move_pen(pen_x, pen_y)




class Pen:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._inner_angle = -60
        self._outer_angle = 90
        self.inner_arm = 8
        self.outer_arm = 8.2


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
        #initializes the starting position of pen. moves pen to start coordinates
        x_start, y_start = start
        self.move_pen(x=x_start, y=y_start)


    def move_pen(self, x=0, y=0): # moving pen to new xy position
        inner_angle, outer_angle = convert_xy_to_angles(x, y)
        set_angles(inner_angle, outer_angle)
        # update current position of a pen and update current angles
        self._update_positions_and_angles(x, y, inner_angle, outer_angle)



class Boundaries:
    def __init__(
            self, left_down_corner = None, right_down_corner = None, left_up_corner = None, right_up_corner = None
    ):
        self._left_down_corner = left_down_corner
        self._right_down_corner = right_down_corner
        self._left_up_corner = left_up_corner
        self._right_up_corner = right_up_corner

    #setters
    def set_left_down_corner(self, x, y):
        self._left_down_corner = (x,y)

    def set_right_down_corner(self, x, y):
        self._right_down_corner = (x,y)

    def set_left_up_corner(self, x, y):
        self._left_up_corner = (x,y)

    def set__right_up_corner(self, x, y):
        self._right_up_corner = (x,y)

    #getters
    def get_left_down_corner(self):
        return self._left_down_corner

    def get_right_down_corner(self):
        return self._right_down_corner

    def get_left_up_corner(self):
        return self._left_up_corner

    def get_right_up_corner(self):
        return self._right_up_corner


    def _check_coordinate_boundaries(self, coordinate):
        x_min = self._left_down_corner[0]
        x_max = self._right_down_corner[0]
        y_min = self._left_down_corner[1]
        y_max = self._left_up_corner[1]

        x, y = coordinate

        #x axis check
        bool_x = ( x >= x_min and x <= x_max )
        #y axis check
        bool_y = ( y >= y_min and y <= y_max )

        if(bool_x and bool_y):
            return True
        else:
            return False


    def check_boundaries(self, start, end):
        #start and end parametrs should be tuples

        #start coordinate
        start_bool = self._check_coordinate_boundaries(start)
        #end coordinate
        end_bool = self._check_coordinate_boundaries(end)

        return start_bool and end_bool



def test(start, end):
    draw_line(start, end)

if __name__ == '__main__':
    boundaries = Boundaries(
        left_down_corner= (-4.7, 5.85),
        right_down_corner = (4.7, 5.85),
        left_up_corner= (-4.7, 15.35),
        right_up_corner=(4.7, 15.35)
    )
    pen = Pen()

    stepper = StepperMotor()
    servo = ServoMotor()

    #test 1
    start = (3, 10)
    end = (3, 6)
    test(start, end)
    #test 2
    start = (3, 8)
    end = (-3, 8)
    test(start, end)
