import pygame
import pytmx
from os import path
from sprites import *
from world import TiledMap


class State:
    def __init__(self, game):
        self.game = game

    def get_map(self):
        return None

    def events(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class SplashState(State):
    def __init__(self, game):
        super().__init__(game)
        self.screen = game.screen
        self.title_font = pygame.font.SysFont("Arial", 55, True)
        self.title_text = self.game.title.split(" ")
        self.instr_font = pygame.font.SysFont("Ariel", 25)
        self.instr_text = "press any key to begin"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.quit()
            elif event.type == pygame.KEYDOWN:
                self.game.change_state(self.game.states['VILLAGE'])

    def draw(self):
        self.screen.fill(0)
        title_top = 10
        for text in self.title_text:
            title = self.title_font.render(text, True, (228,155,15))
            self.screen.blit(title, (10,title_top))
            title_top += title.get_height() + 5
        instruction = self.instr_font.render(self.instr_text, True, (255,255,255))
        instr_top = self.screen.get_height() - instruction.get_height() - 20
        self.screen.blit(instruction, (10, instr_top))
        pygame.display.flip()


class AdventureState(State):
    def __init__(self, game, player, name, camera):
        super().__init__(game)
        #
        # game world
        self.player = player
        self.map = TiledMap(name, game, player)
        self.tile_size = self.map.map.tilewidth
        self.camera = camera
        self.messages = game.messages
        #
        # music
        pygame.mixer.music.load("./sfx/piano-loop.wav")
        pygame.mixer.music.play(-1)

    def get_map(self):
        return self.map

    def events(self):
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) \
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
               self.game.change_state(self.game.states['QUITTING'])

    def update(self):
        self.map.characters.update()
        self.messages.update()
        self.camera.update(self.player)

    def draw(self):
        pygame.display.set_caption(self.game.title + " [{:.2f} FPS]".format(self.game.clock.get_fps()))
        self.game.screen.blit(self.map.underfoot, self.camera.apply(self.map.underfoot.get_rect()))
        for sprite in self.map.characters:
            self.game.screen.blit(sprite.image, self.camera.apply(sprite))
        self.game.screen.blit(self.map.overhead, self.camera.apply(self.map.overhead.get_rect()))
        self.game.screen.blit(self.messages.image, self.messages.rect)
