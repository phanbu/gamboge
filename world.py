import pygame
import pytmx
from os import path
from sprites import *
from state import GameState


class SplashState(GameState):
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
                self.game.adventure()

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


class AdventureState(GameState):
    def __init__(self, game, map_name):
        super().__init__(game)
        self.img_folder = game.img_folder
        #
        # game world
        map_folder = path.join(path.dirname(__file__), 'maps')
        self.world = TiledMap(path.join(map_folder, map_name+'.tmx'), self)
        self.tile_size = self.world.tilemap.tilewidth;
        #
        # sprite groups
        self.characters = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.interacts = pygame.sprite.Group()
        self.messages = pygame.sprite.Group()
        #
        # sprites
        self.world_img_top, self.world_img_bottom = self.world.make_map()
        self.player = Player(self, 20, 20, self.characters)
        self.load_npcs(map_name)
        #
        # camera
        self.camera = Camera(self.world, self.game.screen, self.tile_size)

    def load_npcs(self, map_name):
        with open('npcs.txt') as f:
            for line in f:
                line = line.strip();
                if line:
                    (name, img, npc_map, x, y) = line.split(':')
                    if map_name == npc_map:
                        NPC(self, name, int(x), int(y), img, self.characters, self.obstacles, self.interacts)


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.quit()
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
                self.game.quit()

    def update(self):
        self.characters.update()
        self.messages.update()
        self.camera.update(self.player)

    def draw(self):
        pygame.display.set_caption(self.game.title + " [{:.2f} FPS]".format(self.game.clock.get_fps()))
        self.game.screen.blit(self.world_img_bottom, self.camera.apply(self.world_img_bottom.get_rect()))
        for sprite in self.characters:
            self.game.screen.blit(sprite.image, self.camera.apply(sprite))
        self.game.screen.blit(self.world_img_top, self.camera.apply(self.world_img_top.get_rect()))
        for sprite in self.messages:
            self.game.screen.blit(sprite.image, sprite)


class TiledMap:
    def __init__(self, filename, game):
        self.game = game
        self.tilemap = pytmx.load_pygame(filename, pixelAlpa=True)
        self.width = self.tilemap.width  # in tiles
        self.height = self.tilemap.height  # in tiles

    def render(self, top, bottom):
        surface = bottom
        for layer in self.tilemap.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self.draw_tile_layer(layer, surface)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                self.create_objects(layer)
            if layer.name == 'collision':
                surface = top

    def draw_tile_layer(self, layer, surface):
        tw = self.tilemap.tilewidth
        th = self.tilemap.tileheight
        img = self.tilemap.get_tile_image_by_gid
        for x, y, gid in layer:
            tile = img(gid)
            if tile:
                surface.blit(tile, (x * tw, y * th))
                if layer.name == 'collision':
                    Obstacle(self.game, x, y, self.game.obstacles)

    def create_objects(self, layer):
        print(layer.name, self.tilemap)

    def make_map(self):
        w = self.width * self.tilemap.tilewidth
        h = self.height * self.tilemap.tileheight
        top = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        bottom = pygame.Surface((w, h)).convert()
        self.render(top, bottom)
        return top, bottom


class Camera:
    def __init__(self, world, display: pygame.Surface, tile_size):
        self.tile_size = tile_size
        self.world_width, self.world_height = world.width * self.tile_size, world.height * self.tile_size
        self.display_width, self.display_height = display.get_size()
        self.camera = pygame.Rect(0, 0, world.width, world.height)

    def update(self, target):
        x = -target.rect.centerx + int(self.display_width / 2)
        y = -target.rect.centery + int(self.display_height / 2)
        #
        # don't scroll past the edge of the world in any direction
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.world_width - self.display_width), x)  # right
        y = max(-(self.world_height - self.display_height), y)  # bottom
        self.camera = pygame.Rect(x, y, self.world_width, self.world_height)

    def apply(self, entity):
        if isinstance(entity, pygame.sprite.Sprite):
            return entity.rect.move(self.camera.topleft)
        elif isinstance(entity, pygame.Rect):
            return pygame.Rect((entity.left+self.camera.left, entity.top+self.camera.top), entity.size)
        else:
            raise Exception('cannot apply() on ' + str(entity))
