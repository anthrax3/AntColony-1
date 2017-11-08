from universe.iupdatable import IUpdatable
from universe.isensable import ISensable
from universe.ant import Ant
from universe.actions import LeaveNest
import universe.constants as const


class Nest(IUpdatable, ISensable):
    def __init__(self, num_ants_to_spawn, spawn_period_in_sec, pheromone_intensity):
        self._NUM_ANTS_TO_SPAWN = num_ants_to_spawn
        self._SPAWN_PERIOD_IN_SEC = spawn_period_in_sec
        self._PHEROMONE_INTENSITY = pheromone_intensity
        self._ms_since_last_spawn = 0
        self._num_ants_spawned = 0
        self._ants = []
        self._spawn_ant()

    def update(self, ms_elapsed, context):
        self._ms_since_last_spawn += ms_elapsed
        if self._num_ants_spawned < self._NUM_ANTS_TO_SPAWN and \
           self._SPAWN_PERIOD_IN_SEC < self._ms_since_last_spawn / 1000.0:
            self._spawn_ant()

        context['in_nest'] = True
        for ant in self._ants:
            requested_action = ant.update(ms_elapsed, context)
            if type(requested_action) == LeaveNest:
                self._ants.remove(ant)
                return ant

    def enter_ant(self, ant):
        self._ants.append(ant)

    def get_intensity(self):
        return self._PHEROMONE_INTENSITY

    def _spawn_ant(self):
        self._ants.append(Ant(const.ANT_LENGTH,
                              const.ANT_WIDTH,
                              const.ANT_PHEROMONE_DEPOSIT_RATE_PER_SEC,
                              const.ANT_PHEROMONE_DEPOSIT_INTENSITY_DECAY_FACTOR_PER_SEC,
                              const.ANT_FOOD_PHEROMONE_DECAY_FACTOR_PER_SEC,
                              const.ANT_NEST_PHEROMONE_DECAY_FACTOR_PER_SEC,
                              const.ANT_CHAOS_FACTOR,
                              const.ANT_MOVE_SPEED,
                              const.ANT_HEADING_DELTA_MOMENTUM_FACTOR,
                              const.ANT_MAX_SEARCHING_TIME_IN_SEC,
                              const.ANT_SENSING_RANGE,
                              const.ANT_SENSING_ATTENUATION_GAIN,
                              const.ANT_COLLISION_AVOIDANCE_HEADING_INCREMENT))
        self._ms_since_last_spawn = 0
        self._num_ants_spawned += 1
