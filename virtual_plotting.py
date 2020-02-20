import math
import matplotlib.pyplot as plt

class Triangle:
    '''
    In order to understand namings, see documentation. Page 6, plotting simulation
    '''
    def __init__(self):
        self.inner_angle = 0
        self.alfa = 0
        self.C = (0, 0)
        self.A = self.B = None
        self.xi = self.yi = None
        self.x = self.y = None

    def set_alfa(self, inner_angle):
        alfa = 90 + inner_angle
        self.alfa = alfa

    def find_coordinates(self, pen, A):
        self.xi = math.cos(math.radians(self.alfa)) * pen.inner_arm
        self.yi = math.sin( math.radians(self.alfa) ) * pen.inner_arm

        self.B = (-self.xi, self.yi)

        self.A = A

    def get_coordinates(self):
        return [ self.A[0], self.B[0], self.C[0]] , [self.A[1], self.B[1], self.C[1]]

    def plot(self):

        # naming the x axis
        plt.xlabel('x - axis')
        # naming the y axis
        plt.ylabel('y - axis')
        # giving a title to my graph
        plt.title('Plotter')
        plt.axis([-8, 8, -0, 16])
        plt.grid(True)

        x1 = [ self.A[0], self.B[0], self.C[0] ]
        y1 = [ self.A[1], self.B[1], self.C[1] ]



        point1, = plt.plot([self.A[0]], [self.A[1]], marker='o', markersize=3, color="red")
        point2, = plt.plot([self.B[0]], [self.B[1]], marker='o', markersize=3, color="red")
        point_xy,=plt.plot([self.A[0]], [self.A[1]], marker='o', markersize=1, color="green")
        arms, = plt.plot(x1,y1, color='blue')

        point_list = []
        point_list.append(point1)
        point_list.append(point2)
        point_list.append(arms)

        plt.pause(0.001)
        for p in point_list:
            p.remove()

    def __str__(self):
        msg = 'A: ' + str(self.A) + '\nB: ' + str(self. B) +  '\nC: ' + str(self.C)
        return msg
