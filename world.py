import pygame
import pytmx
from os import path
from sprites import *


class TiledMap:
    def __init__(self, name, game, player=None):
        filename = path.join(path.dirname(__file__), 'maps', name + '.tmx')
        self.map = pytmx.load_pygame(filename, pixelAlpa=True)
        self.width = self.map.width  # in tiles
        self.height = self.map.height  # in tiles
        self.game = game
        self.tile_size = game.tile_size
        #
        # sprite groups
        self.characters = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.interacts = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        if player is not None:
            self.characters.add(player)
        #
        # messages
        self.messages = game.messages
        #
        # sprites
        self._load_npcs(name)
        self._load_exits()
        #
        # images
        self.overhead, self.underfoot = self._render()

    def _render(self):
        w = self.width * self.tile_size.x
        h = self.height * self.tile_size.y
        top = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        bottom = surface = pygame.Surface((w, h)).convert()
        for layer in self.map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._draw_tile_layer(layer, surface)
            if layer.name == 'collision':
                surface = top
        return top, bottom

    def _draw_tile_layer(self, layer, surface):
        img = self.map.get_tile_image_by_gid
        for x, y, gid in layer:
            tile = img(gid)
            if tile:
                tile = pygame.transform.smoothscale(tile, (int(self.tile_size.x), int(self.tile_size.y)))
                surface.blit(tile, (x * self.tile_size.x, y * self.tile_size.y))
                if layer.name == 'collision':
                    Obstacle(self.game, Vector(x, y), self.obstacles)

    def _load_npcs(self, map_name):
        with open('npcs.txt') as f:
            for line in f:
                line = line.strip();
                if line:
                    (name, img, npc_map, x, y) = line.split(':')
                    if map_name == npc_map:
                        NPC(self, name, Vector(int(x), int(y)), img, self.characters, self.obstacles, self.interacts)

    def _load_exits(self):
        exits = self.map.get_layer_by_name('exits')
        for x in exits:
            print(x.x, x.y, x.width, x.height)  # these variables have the information needed to create the exit sprite's rect
            print(x.properties)                 # these properties have the information needed to switch to the next map
            next_state = x.properties['next_state']
            player_x = int(x.properties['player_x'])
            player_y = int(x.properties['player_y'])
            groups = self.exits
            exit = Exit(pygame.Rect(x.x, x.y, x.width, x.height), next_state, Vector(player_x, player_y,), groups)



class Camera:
    def __init__(self, display: pygame.Surface):
        self.tile_size = None
        self.map_width, self.map_height = None, None
        self.camera = None
        self.display_width, self.display_height = display.get_size()

    def set_map(self, map):
        if map is None:
            self.tile_size = None
            self.map_width = self.map_height = None
            self.camera = None
        else:
            self.tile_size = map.tile_size
            self.map_width, self.map_height = map.width * self.tile_size.x, map.height * self.tile_size.y
            self.camera = pygame.Rect(0, 0, map.width, map.height)

    def update(self, target):
        if self.camera is not None:
            x = -target.rect.centerx + int(self.display_width / 2)
            y = -target.rect.centery + int(self.display_height / 2)
            #
            # don't scroll past the edge of the world in any direction
            x = min(0, x)  # left
            y = min(0, y)  # top
            x = max(-(self.map_width - self.display_width), x)  # right
            y = max(-(self.map_height - self.display_height), y)  # bottom
            self.camera = pygame.Rect(x, y, self.map_width, self.map_height)

    def apply(self, entity):
        if self.camera is None:
            return None
        if isinstance(entity, pygame.sprite.Sprite):
            return entity.rect.move(self.camera.topleft)
        elif isinstance(entity, pygame.Rect):
            return pygame.Rect((entity.left+self.camera.left, entity.top+self.camera.top), entity.size)
        else:
            raise Exception('cannot apply() on ' + str(entity))
