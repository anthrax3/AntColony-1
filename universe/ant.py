from universe.iupdatable import IUpdatable
from universe.icollidable import ICollidable
from universe.actions import Move, LeaveNest, EnterNest, DepositPheromone, TurnAround
from universe.pheromone import Pheromone
from universe.food import Food

from lib.sensableregion import SensableRegion

import random as rand
import math


class Ant(IUpdatable, ICollidable):
    _MAX_CHAOTIC_DELTA_HEADING = 0.5 * math.pi

    class State:
        HEADING_HOME = 0
        LOOKING_FOR_FOOD = 1

    def __init__(self,
                 length,
                 width,
                 pheromone_deposit_rate_per_sec,
                 pheromone_deposit_intensity_decay_factor_per_sec,
                 food_pheromone_decay_factor_per_sec,
                 nest_pheromone_decay_factor_per_sec,
                 chaos_factor,
                 move_speed_dist_per_sec,
                 heading_delta_momentum_factor,
                 max_search_time_in_sec,
                 sensing_range,
                 sensing_range_attenuation_gain,
                 collision_avoidance_heading_increment):
        self._LENGTH = length
        self._WIDTH = width
        self._COLLISION_RADIUS = max(0.5 * self._LENGTH, 0.5 * self._WIDTH)
        self._PHEROMONE_DEPOSIT_PERIOD_MS = 1000.0 / pheromone_deposit_rate_per_sec
        self._PHEROMONE_DEPOSIT_INTENSITY_DECAY_FACTOR = pheromone_deposit_intensity_decay_factor_per_sec
        self._FOOD_PHEROMONE_DECAY_FACTOR_PER_SEC = food_pheromone_decay_factor_per_sec
        self._NEST_PHEROMONE_DECAY_FACTOR_PER_SEC = nest_pheromone_decay_factor_per_sec
        self._CHAOS_FACTOR = chaos_factor
        self._MOVE_SPEED_DIST_PER_SEC = move_speed_dist_per_sec
        self._HEADING_DELTA_MOMENTUM_FACTOR = heading_delta_momentum_factor
        self._MAX_SEARCH_TIME_IN_SEC = max_search_time_in_sec
        self._SENSING_RANGE = sensing_range
        self._ATTENUATION_GAIN = sensing_range_attenuation_gain
        self._COLLISION_AVOIDANCE_HEADING_INCREMENT = collision_avoidance_heading_increment
        self._ms_since_pheromone_deposited = 0
        self._pheromone_deposit_intensity = 1.0
        self._seconds_until_turn_around = max_search_time_in_sec
        self._times_turned_around = 0
        self._previous_requested_heading_delta = 0.0
        self._carrying_food = False
        self._state = self.State.LOOKING_FOR_FOOD
        self._state_to_target_type_map = {self.State.HEADING_HOME: Nest,
                                          self.State.LOOKING_FOR_FOOD: Food}
        self._state_to_target_pheromone_type_map = {self.State.HEADING_HOME: Pheromone.Type.NEST,
                                                    self.State.LOOKING_FOR_FOOD: Pheromone.Type.FOOD}

    def update(self, ms_elapsed, context):
        if context['in_nest']:
            self._times_turned_around = 0
            self._seconds_until_turn_around = self._MAX_SEARCH_TIME_IN_SEC
            self._carrying_food = False
            self._pheromone_deposit_intensity = 1.0
            self._state = self.State.LOOKING_FOR_FOOD
            return LeaveNest()
        self._decay_pheromone_deposit_intensity(ms_elapsed)
        self._ms_since_pheromone_deposited += ms_elapsed
        if self._PHEROMONE_DEPOSIT_PERIOD_MS < self._ms_since_pheromone_deposited:
            self._ms_since_pheromone_deposited = 0
            return DepositPheromone(self._produce_pheromone())
        if not self._carrying_food:
            self._seconds_until_turn_around -= 0.001 * ms_elapsed
            if self._seconds_until_turn_around < 0.0:
                self._state = self.State.HEADING_HOME
                self._times_turned_around += 1.0
                self._seconds_until_turn_around = self._MAX_SEARCH_TIME_IN_SEC * 2.0**self._times_turned_around
                return TurnAround()
        if self._state == self.State.LOOKING_FOR_FOOD:
            if self._check_if_food_in_range(context[SensableRegion]):
                self._carrying_food = True
                self._pheromone_deposit_intensity = 1.0
                self._state = self.State.HEADING_HOME
                return TurnAround()
        if self._state == self.State.HEADING_HOME:
            # Enter Nest when in range
            possible_nest = self._check_if_nest_in_range(context[SensableRegion])
            if possible_nest is not None:
                nest_to_enter = possible_nest
                return EnterNest(nest_to_enter)
        requested_heading_delta = self._calculate_heading_delta(context[SensableRegion],
                                                                self._state_to_target_type_map[self._state],
                                                                self._state_to_target_pheromone_type_map[self._state])
        self._previous_requested_heading_delta = requested_heading_delta
        return Move(requested_heading_delta, self._MOVE_SPEED_DIST_PER_SEC)

    def get_collision_radius(self):
        return self._COLLISION_RADIUS

    def _produce_pheromone(self):
        if self._carrying_food:
            pheromone_type = Pheromone.Type.FOOD
            pheromone_decay_factor = self._FOOD_PHEROMONE_DECAY_FACTOR_PER_SEC
        else:
            pheromone_type = Pheromone.Type.NEST
            pheromone_decay_factor = self._NEST_PHEROMONE_DECAY_FACTOR_PER_SEC
        return Pheromone(pheromone_type, self, pheromone_decay_factor, self._pheromone_deposit_intensity)

    def _calculate_heading_delta_looking_for_food(self, sensable_region):
        requested_heading_delta = self._previous_requested_heading_delta * \
                                  self._HEADING_DELTA_MOMENTUM_FACTOR + \
                                  rand.uniform(self._CHAOS_FACTOR * -self._MAX_CHAOTIC_DELTA_HEADING,
                                               self._CHAOS_FACTOR * self._MAX_CHAOTIC_DELTA_HEADING)
        return requested_heading_delta

    def _calculate_heading_delta(self, sensable_region, target_type, target_pheromone_type):
        HALF_SENSING_RANGE = self._SENSING_RANGE * 0.5
        numerator = 0.0
        denominator = 0.001
        for world_object, rlocation in sensable_region.objects_and_radial_locations.items():
            # Only consider objects ahead of us
            if 0.0 < math.cos(rlocation.angle_rad):
                if (type(world_object) == Pheromone and world_object.get_type() == target_pheromone_type) or \
                   type(world_object) == target_type:
                    if rlocation.distance <= HALF_SENSING_RANGE:
                        dist_factor = 1.0 - 0.5 * (rlocation.distance / HALF_SENSING_RANGE)**self._ATTENUATION_GAIN
                    else:
                        dist_factor = 0.5 * (1.0 - (rlocation.distance - HALF_SENSING_RANGE) / HALF_SENSING_RANGE)**self._ATTENUATION_GAIN
                    numerator += world_object.get_intensity() * \
                                 0.5 * math.pi * math.sin(rlocation.angle_rad) * \
                                 math.cos(rlocation.angle_rad)**0.25 * \
                                 dist_factor
                    denominator += world_object.get_intensity()
                ##if issubclass(type(world_object), ICollidable) and \
                ##   rlocation.distance < (self.get_collision_radius() + world_object.get_collision_radius() + 1.0):
                    #if math.sin(rlocation.angle_rad) < 0.0:
                ##    return self._COLLISION_AVOIDANCE_HEADING_INCREMENT
                    #else:
                    #    return -self._COLLISION_AVOIDANCE_HEADING_INCREMENT
        requested_heading_delta = numerator / denominator
        requested_heading_delta += self._previous_requested_heading_delta * self._HEADING_DELTA_MOMENTUM_FACTOR
        requested_heading_delta += rand.uniform(self._CHAOS_FACTOR * -self._MAX_CHAOTIC_DELTA_HEADING,
                                                self._CHAOS_FACTOR * self._MAX_CHAOTIC_DELTA_HEADING)
        return requested_heading_delta

    def _check_if_nest_in_range(self, sensable_region):
        for world_object, rlocation in sensable_region.objects_and_radial_locations.items():
            if type(world_object) == Nest:
                nest = world_object
                if rlocation.distance < self.get_collision_radius():
                    return nest
        return None

    def _check_if_food_in_range(self, sensable_region):
        for world_object, rlocation in sensable_region.objects_and_radial_locations.items():
            if type(world_object) == Food and \
               rlocation.distance < (self.get_collision_radius() + world_object.get_collision_radius() + 1.0):
                return True
        return False

    def _decay_pheromone_deposit_intensity(self, ms_elapsed):
        self._pheromone_deposit_intensity *= self._PHEROMONE_DEPOSIT_INTENSITY_DECAY_FACTOR**(0.001 * ms_elapsed)

# ToDo: improve this when you think of better solution
from universe.nest import Nest
