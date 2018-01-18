import pygame
import pytmx
from os import path
from sprites import Obstacle, Player
from state import GameState


class SplashState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def events(self):
        pass

    def draw(self):
        self.game.adventure()


class AdventureState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.tile_size = 16
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
        self.world_img_top, self.world_img_bottom = self.world.make_map()
        self.player = Player(self, 20, 20, self.characters)
        #
        # camera
        self.camera = Camera(self.world, self.screen, self.tile_size)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.quit()
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
                self.game.quit()

    def update(self):
        self.characters.update()
        self.camera.update(self.player)
        print('updating adventure state')

    def draw(self):
        pygame.display.set_caption(self.title + " [{:.2f} FPS]".format(self.clock.get_fps()))
        self.screen.blit(self.world_img_bottom, self.camera.apply(self.world_img_bottom.get_rect()))
        for sprite in self.characters:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.screen.blit(self.world_img_top, self.camera.apply(self.world_img_top.get_rect()))


class AdventureState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.tile_size = 16
        self.img_folder = game.img_folder
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
        self.world_img_top, self.world_img_bottom = self.world.make_map()
        self.player = Player(self, 20, 20, self.characters)
        #
        # camera
        self.camera = Camera(self.world, self.game.screen, self.tile_size)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.quit()
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
                self.game.quit()

    def update(self):
        self.characters.update()
        self.camera.update(self.player)

    def draw(self):
        pygame.display.set_caption(self.game.title + " [{:.2f} FPS]".format(self.game.clock.get_fps()))
        self.game.screen.blit(self.world_img_bottom, self.camera.apply(self.world_img_bottom.get_rect()))
        for sprite in self.characters:
            self.game.screen.blit(sprite.image, self.camera.apply(sprite))
        self.game.screen.blit(self.world_img_top, self.camera.apply(self.world_img_top.get_rect()))


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