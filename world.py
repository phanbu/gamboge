import pygame
import pytmx
from sprites import Obstacle


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