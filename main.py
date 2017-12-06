import pygame
from os import path
from sprites import *
from world import *


class Game:
    def __init__(self):
        self.playing = True
        self.title = "PockétMonsters: Gamboge"
        self.tile_size = 16
        self.display_width = 500   # 16 * 64 or 32 * 32 or 64 * 16
        self.display_height = 500   # 16 * 48 or 32 * 24 or 64 * 12
        self.fps = 60
        #
        # create screen
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption(self.title)
        #
        # clock
        self.clock = pygame.time.Clock()
        self.delta_t = 0                     # represents the change in time since the last frame (in milliseconds)
        #
        # game images
        self.img_folder = path.join(path.dirname(__file__), 'images')
        #
        # game world
        map_folder = path.join(path.dirname(__file__), 'maps')
        self.world = TiledMap(path.join(map_folder, 'village.tmx'), self)
        #
        # sprite groups
        self.characters = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        #
        # sprites
        self.world_img_top, self.world_img_bottom = self.world.make_map(self)
        self.player = Player(self, 20, 20, self.characters)
        #
        # camera
        self.camera = Camera(self.world, self.screen, self.tile_size)

    def run(self):
        while self.playing:
            self.delta_t = self.clock.tick(self.fps) / 1000.0
            self.events()
            self.update()
            self.draw()

    def quit(self):
        self.playing = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
                self.quit()

    def update(self):
        self.characters.update()
        self.camera.update(self.player)

    def draw(self):
        pygame.display.set_caption(self.title + " [{:.2f} FPS]".format(self.clock.get_fps()))
        self.screen.blit(self.world_img_bottom, self.camera.apply(self.world_img_bottom.get_rect()))
        for sprite in self.characters:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.screen.blit(self.world_img_top, self.camera.apply(self.world_img_top.get_rect()))
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    Game().run()
    pygame.quit()
