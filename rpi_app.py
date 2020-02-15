import math

def set_inner_angle(inner_angle):
    print('inner angle on inner motor is set to: ' + str(inner_angle))
def set_outer_angle(outer_angle):
    print('outer angle on outer motor is set to: ' + str(outer_angle))

def convert_xy_to_angles(x, y):
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

def set_angles(inner_angle, outer_angle):
    #take into consideration the starting angles
    set_inner_angle(inner_angle)
    set_outer_angle(outer_angle)


def move_pen(x=0, y=0):
    inner_angle, outer_angle = convert_xy_to_angles(x, y)
    set_angles(inner_angle, outer_angle)
    pass



def draw_line(start = (0,0), end = (0,0)):
    start_x, start_y = start
    end_x, end_y = end
    length_x = start_x - end_x
    length_y = start_y - end_y
    pen_x, pen_y = pen.get_current_position()

    length = math.sqrt(length_x ** 2 + length_y ** 2) #total length

    number_of_steps = int(length * 100)

    length_of_step_x = length_x / number_of_steps
    length_of_step_y = length_y / number_of_steps


    pen.park(start=start) #move pen so that it's on the start coordinate

    #actual line drawing
    for step in range(number_of_steps):
        pen_x += length_of_step_x
        pen_y += length_of_step_y

        move_pen(pen_x, pen_y)

        pen.set_current_position(pen_x, pen_y) #update current position of a pen





class Pen:
    def __init__(self):
        self._x = 0
        self._y = 0
        self.inner_angle = -60
        self.outer_angle = 90
        self.inner_arm = 8
        self.outer_arm = 8


    def get_current_position(self):
        return (self._x, self._y)
    def set_current_position(self, x, y):
        self._x = x
        self._y = y

    def park(self,start):
        #initializes the starting position of pen. moves pen to start coordinates
        x_start, y_start = start
        move_pen(x=x_start, y=y_start)



if __name__ == '__main__':
    pen = Pen()
    start = (1,3)
    end = (1,1)
    draw_line(start,end)
    print()