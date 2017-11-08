from .drawable import Drawable
from .renderer import Renderer
from universe.pheromone import Pheromone


class View:
    _ANT_LAYER_INDEX = 3
    _PHEROMONE_LAYER_INDEX = 2
    _WORLD_OBJECT_LAYER_INDEX = 1
    _MAP_LAYER_INDEX = 0

    def __init__(self, drawing_surface, world_map):
        self._drawing_surface = drawing_surface
        self._world_map = world_map
        self._renderer = Renderer(self._drawing_surface)
        self._drawable_layers = [[], [], [], []]
        self._drawable_layers[self._MAP_LAYER_INDEX].append(Drawable(world_map, Drawable.Type.WORLD, None))
        self._pheromone_type_to_drawable_type_map = {Pheromone.Type.FOOD: Drawable.Type.FOOD_PHEROMONE,
                                                     Pheromone.Type.NEST: Drawable.Type.NEST_PHEROMONE}

    def draw(self):
        for layer in self._drawable_layers:
            for drawable in layer:
                self._renderer.draw(drawable)

    def update(self):
        self._drawable_layers[self._WORLD_OBJECT_LAYER_INDEX].clear()
        self._drawable_layers[self._ANT_LAYER_INDEX].clear()
        self._drawable_layers[self._PHEROMONE_LAYER_INDEX].clear()
        for nest in self._world_map.get_nests():
            drawable_nest = Drawable(nest, Drawable.Type.NEST, self._world_map.get_drawing_context(nest))
            self._drawable_layers[self._WORLD_OBJECT_LAYER_INDEX].append(drawable_nest)
        for ant in self._world_map.get_ants():
            drawable_ant = Drawable(ant, Drawable.Type.ANT, self._world_map.get_drawing_context(ant))
            self._drawable_layers[self._ANT_LAYER_INDEX].append(drawable_ant)
        for food_source in self._world_map.get_food_sources():
            drawable_food_source = Drawable(food_source, Drawable.Type.FOOD,
                                            self._world_map.get_drawing_context(food_source))
            self._drawable_layers[self._WORLD_OBJECT_LAYER_INDEX].append(drawable_food_source)
        for pheromone in self._world_map.get_pheromones():
            drawable_pheromone = Drawable(pheromone, self._pheromone_type_to_drawable_type_map[pheromone.get_type()],
                                          self._world_map.get_drawing_context(pheromone))
            self._drawable_layers[self._PHEROMONE_LAYER_INDEX].append(drawable_pheromone)
