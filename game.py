import pygame
from os import path
from world import *
from state import *


class Game:
    def __init__(self):
        self.title = "PockétMonsters: Gamboge"
        self.display_width = 500   # 16 * 64 or 32 * 32 or 64 * 16
        self.display_height = 500   # 16 * 48 or 32 * 24 or 64 * 12
        self.fps = 60
        #
        # game images
        self.img_folder = path.join(path.dirname(__file__), 'images')
        #
        # create screen
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption(self.title)
        #
        # clock
        self.clock = pygame.time.Clock()
        self.delta_t = 0
        #
        # camera
        self.camera = Camera(self.screen)
        #
        # game states
        map_folder = path.join(path.dirname(__file__), 'maps')
        self.states = {
            'SPLASH': SplashState(self),
            'VILLAGE': AdventureState(self, TiledMap(path.join(map_folder, 'village')), 'village', self.camera),
            'QUITTING' : None,
        }
        self.state = self.states['SPLASH']

    def run(self):
        while self.state is not None:
            self.delta_t = self.clock.tick(self.fps) / 1000.0
            self.state.events()
            self.state.update()
            self.state.draw()
            pygame.display.flip()


    def change_state(self, state):
        self.state = state
        self.camera.set_map(state.get_map())
