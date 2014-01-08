import matplotlib.pyplot as plt

import os, sys, atexit
os.chdir(os.path.dirname(sys.argv[0]))
atexit.register(lambda destruct: plt.close(), None)

import numpy as np

class MarchingSquares:
    """ Class that contours a matrix of values. """
    def __init__(self, data, r, clevs=[.5]):
        self.data = data
        self.r = r
        self.clevs = clevs
        self.points = []

    def contour(self):
        """ Constructs matrices of binary values representing contours of the data. """
        max_ = np.max(self.data)
        min_ = np.min(self.data)

        #print(window)

        m = self.data.shape[0] - 1 # Rows
        n = self.data.shape[1] - 1 # Cols

        blobs = []

        for c in self.clevs:
            threshold = c * (max_ - min_) / 2 + min_

            points = []

            start = False
            for j in range(m): # For each row...
                for i in range(n): # For each column...
                    top = np.array(self.data[j][i:i+2])
                    bottom = np.array(self.data[j+1][i:i+2])
                    window = np.matrix((top, bottom))

                    window.j = j # Set current row position.
                    window.i = i # Set current column position.
                    window.c = threshold # Set threshold.
                    window._pts = self._translate(window)

                    self._march(window)

            #print(len(self.points))
            blobs.append(self.points)
            self.points = []

        return blobs

    def _translate(self, window):
        r = self.r

        p1 = []
        p1.append(r[window.i])
        p1.append(r[window.j])
        p1.append(window[0,0])

        p2 = []
        p2.append(r[window.i+1])
        p2.append(r[window.j])
        p2.append(window[0,1])

        p3 = []
        p3.append(r[window.i])
        p3.append(r[window.j+1])
        p3.append(window[1,0])

        p4 = []
        p4.append(r[window.i+1])
        p4.append(r[window.j+1])
        p4.append(window[1,1])

        p5 = []
        p5.append((p1[0] + p2[0]) / 2)
        p5.append((p1[1] + p3[1]) / 2)
        #print(np.average([p[2] for p in (p1,p2,p3,p4)]))
        p5.append(np.average([p[2] for p in (p1,p2,p3,p4)]))

        return { "ul":p1, "ur":p2, "ll":p3, "lr":p4, "center":p5 }

    def _march(self, window):
        c = window.c
        pts = window._pts

        ul_over = pts["ul"][2] >= c
        ur_over = pts["ur"][2] >= c
        ll_over = pts["ll"][2] >= c
        lr_over = pts["lr"][2] >= c
        center_over = pts["center"][2] > c

        points = []

        #if (entry != []): print(entry)

        # Detect all 16 cases...
        # 1
        if ul_over and ur_over and ll_over and lr_over:
            pass

        # 2
        elif not ul_over and not ur_over and not ll_over and not lr_over:
            pass

        # 3
        elif ul_over and ur_over and not ll_over and lr_over:
            entry = []
            entry.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            entry.append(pts["ll"][1])

            center = []
            if center_over:
                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["ll"]), c, mode="y"))
            else:
               center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
               center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(pts["ul"][0])
            exit.append(self._interpolate((pts["ll"], pts["ul"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 4
        elif ul_over and ur_over and ll_over and not lr_over:
            entry = []
            entry.append(pts["lr"][0])
            entry.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            center = []
            if center_over:
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="y"))
            else:
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            exit.append(pts["ll"][1])
            

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 5
        elif ul_over and not ur_over and ll_over and lr_over:
            entry = []
            entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            entry.append(pts["ur"][1])

            center = []
            if center_over:
                center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))
            else:
               center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
               center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(pts["lr"][0])
            exit.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 6
        elif not ul_over and ur_over and ll_over and lr_over:
            entry = []
            entry.append(pts["ul"][0])
            entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

            center = []
            if center_over:
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))
            else:
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="y"))

            exit = []
            exit.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            exit.append(pts["ul"][1])

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 7
        elif not ul_over and not ur_over and ll_over and not lr_over:
            entry = []
            entry.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            entry.append(pts["ll"][1])

            center = []
            if center_over:
                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["ll"]), c, mode="y"))
            else:
                center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(pts["ul"][0])
            exit.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 8
        elif not ul_over and not ur_over and not ll_over and lr_over:
            entry = []
            entry.append(pts["ur"][0])
            entry.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            center = []
            if center_over:
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="y"))
            else:
               center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
               center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            exit.append(pts["ll"][1])

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 9
        elif not ul_over and ur_over and not ll_over and not lr_over:
            entry = []
            entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            entry.append(pts["ur"][1])

            center = []
            if center_over:
                center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))
            else:
               center.append(self._interpolate((pts["center"], pts["ur"]), c, mode="x"))
               center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

            exit = []
            exit.append(pts["lr"][0])
            exit.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 10
        elif ul_over and not ur_over and not ll_over and not lr_over:
            entry = []
            entry.append(pts["ul"][0])
            entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

            center = []
            if center_over:
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))
            else:
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="x"))
                center.append(self._interpolate((pts["center"], pts["lr"]), c, mode="y"))

            exit = []
            exit.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            exit.append(pts["ul"][1])

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 11
        elif ul_over and ur_over and not ll_over and not lr_over:
            entry  = []
            entry.append(pts["ul"][0])
            entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

            center = pts["center"][0:2]

            exit = []
            exit.append(pts["ur"][0])
            exit.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            self.points.append(entry)
            #self.points.append(center)
            self.points.append(exit)

        # 12
        elif ul_over and not ur_over and ll_over and not lr_over:
            entry = []
            entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            entry.append(pts["ul"][1])

            center = pts["center"][0:2]

            exit = []
            exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            exit.append(pts["ll"][1])

            self.points.append(entry)
            #self.points.append(center)
            self.points.append(exit)

        # 13
        elif not ul_over and not ur_over and ll_over and lr_over:
            entry = []
            entry.append(pts["ul"][0])
            entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

            center = pts["center"][0:2]

            exit = []
            exit.append(pts["ur"][0])
            exit.append(self._interpolate((pts["ur"], pts["lr"]), c, mode="y"))

            self.points.append(entry)
            #self.points.append(center)
            self.points.append(exit)

        # 14
        elif not ul_over and ur_over and not ll_over and lr_over:
            entry = []
            entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
            entry.append(pts["ul"][1])

            center = pts["center"][0:2]

            exit = []
            exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
            exit.append(pts["ll"][1])

            self.points.append(entry)
            #self.points.append(center)
            self.points.append(exit)

        # 15 - Saddle
        elif not ul_over and ur_over and ll_over and not lr_over:
            print("Bam!")
            entry = []
            center = []
            exit = []

            if center_over:
                entry.append(pts["ul"][0])
                entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

                self.points.append(entry); entry = []

                entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
                entry.append(pts["ul"][1])

                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="y"))

                self.points.append(center); center = []

                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

                exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
                exit.append(pts["ll"][1])

                self.points.append(exit); exit = []

                exit.append(pts["ur"][0])
                exit.append(self._interpolate((pts["lr"], pts["ur"]), c, mode="y"))
            else:
                entry.append(pts["ul"][0])
                entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

                self.points.append(entry); entry = []

                entry.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
                entry.append(pts["ll"][1])

                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))

                self.points.append(center); center = []

                center.append(self._interpolate((pts["lr"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["lr"], pts["center"]), c, mode="y"))

                exit.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
                exit.append(pts["ul"][1])

                self.points.append(exit); exit = []

                exit.append(pts["ur"][0])
                exit.append(self._interpolate((pts["lr"], pts["ur"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

        # 16 - Saddle
        elif ul_over and not ur_over and not ll_over and lr_over:
            print("Bam!")
            entry = []
            center = []
            exit = []

            if center_over:
                entry.append(pts["ul"][0])
                entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

                self.points.append(entry); entry = []

                entry.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
                entry.append(pts["ll"][1])

                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ul"], pts["center"]), c, mode="y"))

                self.points.append(center); center = []

                center.append(self._interpolate((pts["lr"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["lr"], pts["center"]), c, mode="y"))

                exit.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
                exit.append(pts["ul"][1])

                self.points.append(exit); exit = []

                exit.append(pts["ur"][0])
                exit.append(self._interpolate((pts["lr"], pts["ur"]), c, mode="y"))

            else:
                entry.append(pts["ul"][0])
                entry.append(self._interpolate((pts["ul"], pts["ll"]), c, mode="y"))

                self.points.append(entry); entry = []

                entry.append(self._interpolate((pts["ul"], pts["ur"]), c, mode="x"))
                entry.append(pts["ul"][1])

                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ll"], pts["center"]), c, mode="y"))

                self.points.append(center); center = []

                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="x"))
                center.append(self._interpolate((pts["ur"], pts["center"]), c, mode="y"))

                exit.append(self._interpolate((pts["ll"], pts["lr"]), c, mode="x"))
                exit.append(pts["ll"][1])

                self.points.append(exit); exit = []

                exit.append(pts["ur"][0])
                exit.append(self._interpolate((pts["lr"], pts["ur"]), c, mode="y"))

            self.points.append(entry)
            self.points.append(center)
            self.points.append(exit)

    def _interpolate(self, points, threshold, mode):
        #print(points)

        if mode == "x":
            min_x_p = [p for p in points if p[0]==min(points[0][0], points[1][0])][0]
            max_x_p = [p for p in points if p[0]==max(points[0][0], points[1][0])][0]

            difference = max_x_p[0] - min_x_p[0]
            ratio = (max_x_p[2] - threshold) / -(max_x_p[2] - min_x_p[2])
            return min_x_p[0] + ratio * difference

        elif mode == "y":
            min_y_p = [p for p in points if p[1]==min(points[0][1], points[1][1])][0]
            max_y_p = [p for p in points if p[1]==max(points[0][1], points[1][1])][0]

            difference = max_y_p[1] - min_y_p[1]
            ratio = (max_y_p[2] - threshold) / -(max_y_p[2] - min_y_p[2])
            return min_y_p[1] + ratio * difference

def cassini(a, b, r=np.arange(-1.,1.,.02)):
    #r = np.arange(-1.,1.,.04)
    x = np.array([np.float(i) for i in r]); print(len(x))
    y = np.array([np.float(i) for i in r]); print(len(y))
    z = []

    a_sqrd = np.power(a,2)
    b_quad = np.power(b,4)
    x_sqrd = np.power(x,2)
    y_sqrd = np.power(y,2)

    for j in range(len(y)): # Rows
        row = []
        for i in range(len(x)): # Columns
            # Perform 'Ovals of Cassini' function.
            result = _cassini(x_sqrd[i], y_sqrd[j], a_sqrd, b_quad)
            row.append(result)
        z.append(np.array(row))

    return np.array(z)

def _cassini(x, y, a, b):
    FOUR = np.float(4)
    result = np.power((x + y + a),2) - FOUR * a * x - b
    return np.float(result)

if __name__ == "__main__":
    r = np.arange(-1,1,.04)
    grid = cassini(.49, .5, r)

    clevs = [.1,.2,.3,.4,.5,.6,.7,.8,.9]
    ms = MarchingSquares(grid, r, clevs)
    blobs = ms.contour()

    print(len(blobs[0]))

    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import pylab
    polygons = []

    import random

    offset = 1. / len(clevs)
    colors = []
    for i in range(len(clevs)):
        colors.append((random.randint(0, 255)/255., random.randint(0, 255)/255., random.randint(0, 255)/255.))

    blobs.reverse()
    for i in range(len(blobs)):
        b = blobs[i]
        
        # Compute centroid.
        cent=(sum([p[0] for p in b])/len(b),sum([p[1] for p in b])/len(b))
        
        # Sort by polar angle.
        b.sort(key=lambda p: math.atan2(p[1]-cent[1],p[0]-cent[0]))

        #x = np.array([p[0] for p in b])
        #y = np.array([p[1] for p in b])

        #plt.plot(x,y,'-',color=colors[i])

        # plot points
        pylab.scatter([p[0] for p in b],[p[1] for p in b])
        # plot polyline
        pylab.gca().add_patch(patches.Polygon(b,closed=True,fill=True,color=colors[i]))
        #pylab.grid()

    plt.xlim([-.9, .9])
    plt.show()