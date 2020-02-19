from linedraw import *
import matplotlib.pyplot as plt
from boundaries import Boundaries
import json
# ======================user friendly methods for working with lines================
# ==================================================================================
# uses linedraw.py which contains methods for working with images and converting them to json
class Photo:
    def __init__(self, photo_name):
        self._photo_name = photo_name
        self._folder_path = json_folder
        self._path = self._folder_path + self._photo_name
        self._lines = None

    def convert_to_lines(self, boundaries=None):

        '''
        this method should not be called on rpi.
        this is very heavy to execute and has a lot of calculations.
        Called that method only from pc.
        '''
        # ======first save=======
        # =======================
        image_to_json(self._photo_name, draw_contours=3, draw_hatch=40)

        # ======second save======
        # =======================
        # read json file
        with open(self._path + '.json', 'r') as json_photo:
            data = json_photo.read()
        obj = json.loads(data)

        # parse file
        lines = json.loads(data)

        #for some reason 3rd party linedraw.py is strangly saving coordinates. Therefore resize in needed.

        self._lines = self._resize_lines(lines, boundaries)

        with open(self._path + '.json', 'w', encoding='utf-8') as f:
            json.dump(self._lines, f, ensure_ascii=False, indent=4)


    def _resize_lines(self, lines, boundaries):
        '''
        We will slitely modify list of lines and scale those nubmers.
        Now it returns a list of lines, each consisted of list of points.
        Point is now tuple instead of a list
        ===============================================================================================
                        [                     list of lines                                           ]
                        [ [               line            ] , [           line                ] ,...  ]
        list_of_lines = [ [ (x,y) , (x,y) , (x,y) , (x,y) ] , [ (x,y) , (x,y) , (x,y) , (x,y) ] ,...  ]
        ================================================================================================

        We have to improve ratio.

        Then we have to find the maximum coordinates.
        After that comes resizing to our coordinate system.
        Resizing depends on arms length and maximum coordinate that we've previously found
        '''


        # ===helper functions===
        # ======================

        def improve_ratio():
            resized_lines = []
            for line in lines:
                resized_line = []
                for dot in line:
                    x, y = dot[0] * 800 / 1024 - 400, -(dot[1] * 800 / 1024 - 400)
                    resized_line.append( (x, y))
                resized_lines.append(resized_line)

            return resized_lines


        def scale_photo(resized_lines):
            '''
            find resizing / scaling factor
            resize every coordinate
            keeps the photo ratio untouched
            '''

            x_min = x_max = resized_lines[0][0][0]  # resized_lines[0][0][0] returns first x coordinate
            y_min = y_max = resized_lines[0][0][1]  # resized_lines[0][0][1] returns first y coordinate

            for line in resized_lines:
                for dot in line:
                    x, y = dot
                    x_min = min(x, x_min)
                    x_max = max(x, x_max)
                    y_min = min(y, y_min)
                    y_max = max(y, y_max)

            image_x_length = x_max - x_min
            image_y_length = y_max - y_min
            boundaries_x_length = boundaries.get_x_length()
            boundaries_y_length = boundaries.get_y_length()

            RESIZING_FACTOR_X = image_x_length / boundaries_x_length
            RESIZING_FACTOR_Y = image_y_length / boundaries_y_length
            RESIZING_FACTOR = max(RESIZING_FACTOR_X, RESIZING_FACTOR_Y)

            new_resized_lines = []
            for line in resized_lines:
                new_line = []
                for dot in line:
                    x, y = dot
                    x = x / RESIZING_FACTOR
                    y = y / RESIZING_FACTOR
                    new_line.append((x,y))
                new_resized_lines.append(new_line)

            return new_resized_lines

        def move_inside_boundaries(resized_lines):
            frame_left_down_coordinate = boundaries.get_left_down_corner()
            image_left_down_coordinate = None

            x_min, y_min = resized_lines[0][0]
            for line in resized_lines:
                for dot in line:
                    x, y = dot
                    x_min = min(x_min, x)
                    y_min = min(y_min, y)
            image_left_down_coordinate = (x_min, y_min)


            x_diff = y_diff = None
            # we have to find x_diff. x_diff represents how much should every point be moved on x-axis
            # x-axis
            x1 = image_left_down_coordinate[0]
            x2 = frame_left_down_coordinate[0]
            if x1 > x2:
                x_diff = -(abs(x1 - x2))
            else:
                x_diff =   abs(x1 - x2)

            # we have to find y_diff. y_diff represents how much should every point be moved on y-axis
            # y-axis
            y1 = image_left_down_coordinate[1]
            y2 = frame_left_down_coordinate[1]
            if y1 > y2:
                y_diff = -(abs(y1 - y2))
            else:
                y_diff =   abs(y1 - y2)

            new_resized_lines = []
            for line in resized_lines:
                new_line = []
                for dot in line:
                    x, y = dot
                    x += x_diff
                    y += y_diff
                    new_line.append((x,y))
                new_resized_lines.append(new_line)

            return new_resized_lines



        # calling helper functions
        resized_lines = improve_ratio()

        if boundaries is not None:
            resized_lines = scale_photo(resized_lines)
            resized_lines = move_inside_boundaries(resized_lines)

        return resized_lines


    def get_lines(self):
        '''
        returns list of lines, where one line is consisted of tuples (x, y)

        When reading JSON file it returns a list of lines, each of which is a list of points. Like this:
        ===============================================================================================
                        [                     list of lines                                           ]
                        [ [               line            ] , [           line                ] ,...  ]
        list_of_lines = [ [ [x,y] , [x,y] , [x,y] , [x,y] ] , [ [x,y] , [x,y] , [x,y] , [x,y] ] ,...  ]
        ================================================================================================
        '''

        # if resizing was done, there is not a reason to do it once more
        if (self._lines is not None):
            return self._lines

        #else code. If resizing isn't done. Resizing is must have
        # read json file
        with open(self._path + '.json', 'r') as json_photo:
            data = json_photo.read()
        lines = json.loads(data)

        #keep lines in memory so that we dont have to read json object more then once
        self._lines = lines

        return self._lines



    def plot_dots(self):
        lines = self.get_lines()
        # naming the x axis
        plt.xlabel('x - axis')
        # naming the y axis
        plt.ylabel('y - axis')
        # giving a title to my graph
        plt.title('Plotter')
        #plt.axis([-8, 8, -0, 16])
        plt.grid(True)

        #plotting boundaries

        plt.plot(boundaries.get_left_down_corner()[0], boundaries.get_left_down_corner()[1], marker='o', markersize=2, color="red" )
        plt.plot(boundaries.get_left_up_corner()[0], boundaries.get_left_up_corner()[1], marker='o', markersize=2, color="red" )
        plt.plot(boundaries.get_right_down_corner()[0], boundaries.get_right_down_corner()[1], marker='o', markersize=2, color="red" )
        plt.plot(boundaries.get_right_up_corner()[0], boundaries.get_right_up_corner()[1], marker='o', markersize=2, color="red" )

        # plotting dots
        for line in lines:
            x_list = []
            y_list = []
            for dot in line:
                x , y = dot
                x_list.append(x)
                y_list.append(y)

            plt.plot(x_list, y_list, color='blue')
            plt.pause(0.001)
        pass


        plt.show()




if __name__ == '__main__':

    boundaries = Boundaries(
        left_down_corner= (-4.7, 5.85),
        right_down_corner = (4.7, 5.85),
        left_up_corner= (-4.7, 15.35),
        right_up_corner=(4.7, 15.35)
    )
    photo = Photo('africa')
    #photo.convert_to_lines(boundaries)
    photo.plot_dots()

