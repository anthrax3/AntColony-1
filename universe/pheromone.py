from universe.iupdatable import IUpdatable
from universe.isensable import ISensable


class Pheromone(IUpdatable, ISensable):
    class Type:
        NEST = 0
        FOOD = 1

    def __init__(self, pheromone_type, produced_by, decay_factor_per_sec, intensity):
        self._type = pheromone_type
        self._produced_by = produced_by
        self._DECAY_FACTOR = decay_factor_per_sec
        self._intensity = intensity

    def update(self, ms_elapsed, context):
        self._intensity *= self._DECAY_FACTOR**(ms_elapsed / 1000.0)

    def get_type(self):
        return self._type

    def get_producer(self):
        return self._produced_by

    def get_intensity(self):
        return self._intensity
