import matplotlib.pyplot as plt

class Figure:
    """ Class representing a two-dimensional plot. """
    def __init__(self, data, labels=("X", "Y"), mode="bo"):
        """ Initializes a Figure object. """
        self.x = data["x"]
        self.y = data["y"]
        self.xlab = labels[0]
        self.ylab = labels[1]
        self.mode = mode
