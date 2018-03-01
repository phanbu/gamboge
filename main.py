import pygame
from os import path
from world import *
from sound_effects import *


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
        # game states
        self.splash_state = SplashState(self)
        self.adventure_state = AdventureState(self, 'village')
        self.state = self.splash_state

    def run(self):
        while self.state is not None:
            self.delta_t = self.clock.tick(self.fps) / 1000.0
            self.state.events()
            self.state.update()
            self.state.draw()
            pygame.display.flip()

    def adventure(self):
        self.state = self.adventure_state   

    def quit(self):
        self.state = None


if __name__ == "__main__":
    pygame.init()
    Game().run()
    pygame.quit()
