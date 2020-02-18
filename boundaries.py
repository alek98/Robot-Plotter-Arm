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
        # checks if line from start coordinate to end coordinate is inside the drawable area
        #start and end parametrs should be tuples

        #check if start coordinate is inside drawable area
        start_bool = self._check_coordinate_boundaries(start)
        #check if end coordinate is inside drawable area
        end_bool = self._check_coordinate_boundaries(end)

        return start_bool and end_bool

    #not used? check it
    def find_corners(self):
        x_min = self._left_down_corner[0]
        x_max = self._right_down_corner[0]
        y_min = self._left_down_corner[1]
        y_max = self._left_up_corner[1]


        return x_min, x_max, y_min, y_max

    def get_x_length(self):
        x_min = self._left_down_corner[0]
        x_max = self._right_down_corner[0]
        return x_max - x_min

    def get_y_length(self):
        y_min = self._left_down_corner[1]
        y_max = self._left_up_corner[1]
        return y_max - y_min