from universe.iupdatable import IUpdatable
from universe.ant import Ant
from universe.nest import Nest
from universe.food import Food
from universe.pheromone import Pheromone
from universe.actions import Move, TurnAround, DepositPheromone, EnterNest
import universe.constants as const

import lib.computations as compute
from lib.location import Location
from lib.orientation import Orientation
from lib.sensableregion import SensableRegion

import copy
import random as rand
import math


class World(IUpdatable):
    def __init__(self,
                 width,
                 height,
                 num_ants_to_spawn,
                 ant_spawn_period,
                 num_food_sources,
                 food_min_dist_to_nest,
                 food_min_dist_to_world_edge,
                 max_move_duration_in_sec):
        self._width = width
        self._height = height
        self._objects_at_locations = [[[] for _ in range(width)] for _ in range(height)]
        self._MAX_MOVE_DURATION_IN_SEC = max_move_duration_in_sec
        self._action_processing_methods = {None: self._process_no_action,
                                           Move: self._process_move_action,
                                           TurnAround: self._process_turn_around_action,
                                           DepositPheromone: self._process_deposit_pheromone_action,
                                           EnterNest: self._process_enter_nest_action}
        self._drawing_context_creation_methods = {Ant: self._create_drawing_context_for_ant,
                                                  Nest: self._create_drawing_context_for_nest,
                                                  Food: self._create_drawing_context_for_food,
                                                  Pheromone: self._create_drawing_context_for_pheromone}
        self._get_object_location_methods = {Ant: self._get_location_of_ant,
                                             Nest: self._get_location_of_nest,
                                             Food: self._get_location_of_food_source,
                                             Pheromone: self._get_location_of_pheromone}
        self._nests_and_orientations = {}
        the_nest = Nest(num_ants_to_spawn, ant_spawn_period, const.NEST_PHEROMONE_INTENSITY)
        self._nests_and_orientations[the_nest] = Orientation(0.5 * float(width), 0.5 * float(height), 0.0)
        for nest, nest_orientation in self._nests_and_orientations.items():
            self._add_object_at_location(nest, nest_orientation.location)
        self._ants_and_orientations = {}
        self._pheromones_and_locations = {Pheromone.Type.FOOD: {}, Pheromone.Type.NEST: {}}
        self._food_sources_and_locations = {}
        for i in range(num_food_sources):
            self._spawn_food(food_min_dist_to_nest, food_min_dist_to_world_edge)

    def get_drawing_context(self, world_object):
        try:
            return self._drawing_context_creation_methods[type(world_object)](world_object)
        except (KeyError, NameError):
            return {}

    def get_ants(self):
        return self._ants_and_orientations.keys()

    def get_nests(self):
        return self._nests_and_orientations.keys()

    def get_food_sources(self):
        return self._food_sources_and_locations.keys()

    def get_pheromones(self):
        return self._pheromones_and_locations[Pheromone.Type.FOOD].keys() | \
               self._pheromones_and_locations[Pheromone.Type.NEST].keys()

    def update(self, ms_elapsed, context):
        pheromones_to_remove = []
        for pheromone in self.get_pheromones():
            context_for_pheromone = {}
            pheromone.update(ms_elapsed, context_for_pheromone)
            if pheromone.get_intensity() < 0.01:
                pheromones_to_remove.append(pheromone)
        for pheromone_to_remove in pheromones_to_remove:
            pheromone_location = self._pheromones_and_locations[pheromone_to_remove.get_type()][pheromone_to_remove]
            self._remove_object_at_location(pheromone_to_remove, pheromone_location)
            self._pheromones_and_locations[pheromone_to_remove.get_type()].pop(pheromone_to_remove)

        for nest in self._nests_and_orientations.keys():
            context_for_nest = {}
            context_for_nest[SensableRegion] = self._create_sensable_region(self._nests_and_orientations[nest],
                                                                            const.NEST_SENSING_RADIUS,
                                                                            nest)
            possible_ant = nest.update(ms_elapsed, context_for_nest)
            if type(possible_ant) == Ant:
                self._ants_and_orientations[possible_ant] = Orientation(self._nests_and_orientations[nest].location.x,
                                                                        self._nests_and_orientations[nest].location.y,
                                                                        rand.uniform(0.0, 2.0 * math.pi))
                self._add_object_at_location(possible_ant, self._ants_and_orientations[possible_ant].location)

        ants_to_remove = []
        for ant in self._ants_and_orientations.keys():
            context_for_ant = {}
            context_for_ant[SensableRegion] = self._create_sensable_region(self._ants_and_orientations[ant],
                                                                           const.ANT_SENSING_RANGE,
                                                                           ant)
            context_for_ant['in_nest'] = False
            requested_action = ant.update(ms_elapsed, context_for_ant)
            if type(requested_action) == EnterNest:
                ants_to_remove.append(ant)
            self._process_ant_action(ant, requested_action, ms_elapsed)
        for ant in ants_to_remove:
            self._remove_object_at_location(ant, self._ants_and_orientations[ant].location)
            self._ants_and_orientations.pop(ant)

    def _process_ant_action(self, ant, requested_action, ms_elapsed):
        self._action_processing_methods[type(requested_action)](ant, requested_action, ms_elapsed)

    def _process_no_action(self, ant, none_action, ms_elapsed):
        pass

    def _process_move_action(self, acting_ant, move_action, ms_elapsed):
        t = min(ms_elapsed / 1000.0, self._MAX_MOVE_DURATION_IN_SEC)
        self._ants_and_orientations[acting_ant].heading_rad += move_action.heading_delta
        # We need to check for and disregard moves that result in a collision or going out of bounds
        attempted_x = self._ants_and_orientations[acting_ant].location.x + \
                      math.sin(self._ants_and_orientations[acting_ant].heading_rad) * move_action.move_speed * t
        attempted_y = self._ants_and_orientations[acting_ant].location.y + \
                      math.cos(self._ants_and_orientations[acting_ant].heading_rad) * -move_action.move_speed * t
        attempted_location = Location(attempted_x, attempted_y)
        if attempted_location.x < 0 + acting_ant.get_collision_radius() or \
           self._width - acting_ant.get_collision_radius() < attempted_location.x or \
           attempted_location.y < 0 + acting_ant.get_collision_radius() or \
           self._height - acting_ant.get_collision_radius() < attempted_location.y:
            # Nothing left to do when move goes out of bounds
            return
        ##for other_ant, other_orientation in self._ants_and_orientations.items():
        ##    if other_ant == acting_ant:
        ##        continue
        ##    if self._detect_collision(attempted_location, acting_ant.get_collision_radius(),
        ##                              other_orientation.location, other_ant.get_collision_radius()):
        ##        # Nothing left to do when a collision is detected
        ##        return
        for food_source, food_location in self._food_sources_and_locations.items():
            if self._detect_collision(attempted_location, acting_ant.get_collision_radius(),
                                      food_location, food_source.get_collision_radius()):
                # Nothing left to do when a collision is detected
                return
        # If we get here it means the move was valid
        self._remove_object_at_location(acting_ant, self._ants_and_orientations[acting_ant].location)
        self._ants_and_orientations[acting_ant].location.x = attempted_location.x
        self._ants_and_orientations[acting_ant].location.y = attempted_location.y
        self._add_object_at_location(acting_ant, self._ants_and_orientations[acting_ant].location)

    def _process_turn_around_action(self, ant, turn_around_action, ms_elapsed):
        self._ants_and_orientations[ant].heading_rad += math.pi

    def _process_enter_nest_action(self, ant, enter_nest_action, ms_elapsed):
        enter_nest_action.nest.enter_ant(ant)

    def _process_deposit_pheromone_action(self, ant, deposit_pheromone_action, ms_elapsed):
        pheromone = deposit_pheromone_action.pheromone
        location = copy.deepcopy(self._ants_and_orientations[ant].location)
        self._pheromones_and_locations[pheromone.get_type()][pheromone] = location
        self._add_object_at_location(pheromone, location)

    def _create_drawing_context_for_ant(self, ant):
        return {Orientation: self._ants_and_orientations[ant]}

    def _create_drawing_context_for_nest(self, nest):
        return {Location: self._nests_and_orientations[nest].location}

    def _create_drawing_context_for_food(self, food):
        return {Location: self._food_sources_and_locations[food]}

    def _create_drawing_context_for_pheromone(self, pheromone):
        return {Location: self._pheromones_and_locations[pheromone.get_type()][pheromone]}

    def _spawn_food(self, min_dist_to_nest, min_dist_to_world_edge):
        loc_x = 0.0
        loc_y = 0.0
        suitable_loc_found = False
        while not suitable_loc_found:
            loc_x = rand.randrange(min_dist_to_world_edge, float(self._width) - min_dist_to_world_edge)
            loc_y = rand.randrange(min_dist_to_world_edge, float(self._height) - min_dist_to_world_edge)
            suitable_loc_found = True
            for nest_orientation in self._nests_and_orientations.values():
                nest_loc = nest_orientation.location
                dist_to_this_nest_loc = ((loc_x - nest_loc.x)**2.0 + (loc_y - nest_loc.y)**2.0)**0.5
                suitable_loc_found &= min_dist_to_nest < dist_to_this_nest_loc
        food_source = Food(const.FOOD_WIDTH, const.FOOD_HEIGHT, const.FOOD_PHEROMONE_INTENSITY)
        location = Location(loc_x, loc_y)
        self._food_sources_and_locations[food_source] = location
        self._add_object_at_location(food_source, location)

    def _create_sensable_region(self, orientation, radius, target_object):
        sensable_region = SensableRegion()
        bbox_x1 = max(0, int(orientation.location.x - radius))
        bbox_x2 = min(self._width, math.ceil(orientation.location.x + radius))
        bbox_y1 = max(0, int(orientation.location.y - radius))
        bbox_y2 = min(self._height, math.ceil(orientation.location.y + radius))
        for row in self._objects_at_locations[bbox_y1:bbox_y2]:
            for objects_list in row[bbox_x1:bbox_x2]:
                for world_object in objects_list:
                    if world_object is target_object:
                        continue
                    loc_of_object = self._get_object_location_methods[type(world_object)](world_object)
                    dist_of_obj = compute.euclidean_distance(orientation.location, loc_of_object)
                    if dist_of_obj < radius:
                        heading = compute.heading_of_line(orientation.location, loc_of_object)
                        angle_rad = heading - orientation.heading_rad
                        sensable_region.add_object(world_object, angle_rad, dist_of_obj)
        return sensable_region

    def _detect_collision(self, loc_a, collision_rad_a, loc_b, collision_rad_b):
        d = compute.euclidean_distance(loc_a, loc_b)
        return d < (collision_rad_a + collision_rad_b)

    def _add_object_at_location(self, world_object, location):
        x = int(location.x)
        y = int(location.y)
        if world_object not in self._objects_at_locations[y][x]:
            self._objects_at_locations[y][x].append(world_object)

    def _remove_object_at_location(self, world_object, location):
        x = int(location.x)
        y = int(location.y)
        if world_object in self._objects_at_locations[y][x]:
            self._objects_at_locations[y][x].remove(world_object)

    def _get_location_of_ant(self, ant):
        return self._ants_and_orientations[ant].location

    def _get_location_of_nest(self, nest):
        return self._nests_and_orientations[nest].location

    def _get_location_of_food_source(self, food_source):
        return self._food_sources_and_locations[food_source]

    def _get_location_of_pheromone(self, pheromone):
        return self._pheromones_and_locations[pheromone.get_type()][pheromone]
