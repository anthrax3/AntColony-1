from lib.location import Location


class Orientation:
    def __init__(self, x_loc, y_loc, heading_rad):
        self.location = Location(x_loc, y_loc)
        self.heading_rad = heading_rad
