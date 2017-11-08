import math


def euclidean_distance(loc_a, loc_b):
    return ((loc_a.x - loc_b.x)**2.0 + (loc_a.y - loc_b.y)**2.0)**0.5


def heading_of_line(start_loc, end_loc):
    if start_loc.x < end_loc.x:
        # keep in mind that y = 0 at the top of the drawing surface and increases in value as we move down the screen
        return 0.5 * math.pi - math.atan((start_loc.y - end_loc.y) / (end_loc.x - start_loc.x))
    elif start_loc.x == end_loc.x:
        if start_loc.y < end_loc.y:
            return math.pi
        return 0.0
    else:
        # keep in mind that y = 0 at the top of the drawing surface and increases in value as we move down the screen
        return 1.5 * math.pi - math.atan((start_loc.y - end_loc.y) / (end_loc.x - start_loc.x))
