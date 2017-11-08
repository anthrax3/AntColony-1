from .drawable import Drawable
import universe.constants as const
from lib.location import Location
from lib.orientation import Orientation

import pygame
import math


class Renderer:
    def __init__(self, drawing_surface):
        self._drawing_surface = drawing_surface
        self._draw_methods = {Drawable.Type.WORLD: self._draw_world,
                              Drawable.Type.ANT: self._draw_ant,
                              Drawable.Type.NEST: self._draw_nest,
                              Drawable.Type.FOOD: self._draw_food,
                              Drawable.Type.FOOD_PHEROMONE: self._draw_pheromone,
                              Drawable.Type.NEST_PHEROMONE: self._draw_pheromone}

    def draw(self, drawable_item):
        self._draw_methods[drawable_item.get_type()](drawable_item.get_desired_colour(),
                                                     drawable_item.get_drawing_context())

    def _draw_world(self, colour, drawing_context):
        self._drawing_surface.fill(colour)

    def _draw_ant(self, colour, drawing_context):
        location = drawing_context[Orientation].location
        heading = drawing_context[Orientation].heading_rad
        half_ant_length = 0.5 * const.ANT_LENGTH
        d_x = round(math.sin(heading) * half_ant_length)
        d_y = round(math.cos(heading) * half_ant_length)
        fore_end_coords = (location.x + d_x, location.y - d_y)
        aft_end_coords = (location.x - d_x, location.y + d_y)
        pygame.draw.line(self._drawing_surface, colour, aft_end_coords, fore_end_coords, int(const.ANT_WIDTH))

    def _draw_nest(self, colour, drawing_context):
        location = drawing_context[Location]
        half_nest_height = int(0.5 * const.NEST_HEIGHT)
        pygame.draw.line(self._drawing_surface,
                         colour,
                         (location.x, location.y - half_nest_height),
                         (location.x, location.y + half_nest_height),
                         int(const.NEST_WIDTH))

    def _draw_food(self, colour, drawing_context):
        location = drawing_context[Location]
        half_food_height = int(0.5 * const.FOOD_HEIGHT)
        pygame.draw.line(self._drawing_surface,
                         colour,
                         (location.x, location.y - half_food_height),
                         (location.x, location.y + half_food_height),
                         int(const.FOOD_WIDTH))

    def _draw_pheromone(self, colour, drawing_context):
        location = drawing_context[Location]
        pygame.draw.line(self._drawing_surface, colour, (location.x, location.y), (location.x, location.y), 1)
