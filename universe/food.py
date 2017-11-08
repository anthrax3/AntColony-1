from universe.icollidable import ICollidable
from universe.isensable import ISensable


class Food(ICollidable, ISensable):
    def __init__(self, width, length, pheromone_intensity):
        self._WIDTH = width
        self._LENGTH = length
        self._PHEROMONE_INTENSITY = pheromone_intensity
        self._collision_radius = max(0.5 * self._LENGTH, 0.5 * self._WIDTH) - 1.0

    def get_collision_radius(self):
        return self._collision_radius

    def get_intensity(self):
        return self._PHEROMONE_INTENSITY
