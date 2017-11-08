import pygame
import pygame.locals
from universe.world import World
from graphics.view import View

FPS = 10
WIDTH = 480
HEIGHT = 480
NUM_ANTS_TO_SPAWN = 24
ANT_SPAWN_PERIOD = 10
NUM_FOOD_SOURCES = 3
FOOD_MIN_DISTANCE_TO_NEST = 125.0
FOOD_MIN_DISTANCE_TO_WORLD_EDGE = 5.0
MAX_MOVE_DURATION_IN_SEC = 1.0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    world = World(WIDTH, HEIGHT, NUM_ANTS_TO_SPAWN, ANT_SPAWN_PERIOD,
                  NUM_FOOD_SOURCES, FOOD_MIN_DISTANCE_TO_NEST, FOOD_MIN_DISTANCE_TO_WORLD_EDGE,
                  MAX_MOVE_DURATION_IN_SEC)
    world_view = View(screen, world)

    exit_requested = False
    while not exit_requested:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_requested = True
        ms_elapsed = clock.tick(FPS)
        context_for_world = {}
        world.update(ms_elapsed, context_for_world)
        world_view.update()
        world_view.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
