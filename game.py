import pygame
from os import path
from state import *
from world import Camera


class Game:
    def __init__(self):
        self.title = "PockétMonsters: Gamboge"
        self.display_width = 500   # 16 * 64 or 32 * 32 or 64 * 16
        self.display_height = 500   # 16 * 48 or 32 * 24 or 64 * 12
        self.tile_size = Vector(32, 32)
        self.fps = 60
        #
        # create screen
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption(self.title)
        #
        # clock
        self.clock = pygame.time.Clock()
        self.delta_t = 0
        #
        # camera and messages
        self.camera = Camera(self.screen)
        self.messages = MessageBox()
        self.player = Player(self, self.tile_size)
        #
        # game states
        self.states = {
            'SPLASH': SplashState(self),
            'VILLAGE': AdventureState(self, self.player, 'village', self.camera),
            'FOREST': AdventureState(self, self.player, 'forest', self.camera),
            'QUITTING': None,
        }
        self.state = self.states['SPLASH']

    def run(self):
        while self.state is not None:
            self.delta_t = self.clock.tick(self.fps) / 1000.0
            self.state.update()
            self.state.draw()
            pygame.display.flip()
            self.state.events()

    def change_state(self, state):
        self.state = state
        if state is not None:
            self.camera.set_map(state.get_map())
