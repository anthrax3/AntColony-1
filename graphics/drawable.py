from .colourlib import Colours


class Drawable:
    class Type:
        WORLD = 0
        ANT = 1
        FOOD = 2
        NEST = 3
        NEST_PHEROMONE = 4
        FOOD_PHEROMONE = 5

    def __init__(self, object_represented, drawable_type, drawing_context):
        self._object_represented = object_represented
        self._drawable_type = drawable_type
        self._colour = (0, 0, 0)
        if Drawable.Type.WORLD == drawable_type:
            self._colour = Colours.LIGHT_GREY
        if Drawable.Type.ANT == drawable_type:
            self._colour = Colours.BLACK
        if Drawable.Type.NEST == drawable_type:
            self._colour = Colours.BLUE
        if Drawable.Type.FOOD == drawable_type:
            self._colour = Colours.BROWN
        if Drawable.Type.FOOD_PHEROMONE == drawable_type:
            self._colour = Colours.RED
        if Drawable.Type.NEST_PHEROMONE == drawable_type:
            self._colour = Colours.GREEN
        self._context = drawing_context

    def get_object_represented(self):
        return self._object_represented

    def get_type(self):
        return self._drawable_type

    def get_desired_colour(self):
        return self._colour

    def get_drawing_context(self):
        return self._context

    def set_drawing_context(self, context):
        self._context = context
