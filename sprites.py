import pygame
from os import path
from spritesheet import *

Vector = pygame.math.Vector2

DIRECTIONS = {
    'down': Vector(0, 1),
    'up': Vector(0, -1),
    'left': Vector(-1, 0),
    'right': Vector(1, 0),
    'stop': Vector(0, 0)
}


class Character(pygame.sprite.Sprite):
    def __init__(self, game, x, y, *groups):
        super().__init__(groups)
        self.game = game
        self.current_move = self.position = Vector(x, y)
        self.facing = 'down'
        self.is_moving = False
        self.move_anim = 'stop'
        self.started_moving = None
        self.millis_per_grid_sq = 100
        self.rect = None

    def start_moving(self, direction):
        if not self.is_moving:
            self.started_moving = pygame.time.get_ticks()
            self.facing = direction
            self.is_moving = True
            self.current_move = self.position + DIRECTIONS[self.facing]
            if pygame.sprite.spritecollide(self, self.game.obstacles, False, _test_collision):
                self.current_move = self.position
                self.is_moving = False

    def update(self):
        if self.is_moving:
            ticks = pygame.time.get_ticks() - self.started_moving
            diff = min(ticks / self.millis_per_grid_sq, 1.0)
            distance = diff * DIRECTIONS[self.facing]
            self.move_rect(self.position, distance)
            if diff == 1.0:
                self.position = self.current_move
                self.is_moving = False

    def move_rect(self, position, distance=Vector(0, 0)):
        ts = self.game.tile_size
        loc = (self.position * ts) + (distance * ts)
        self.rect.bottomleft = (loc.x, loc.y + ts)


class Player(Character):
    def __init__(self, game, x, y, *groups):
        super().__init__(game, x, y, groups)
        self.player_img = path.join(self.game.img_folder, 'p017.png')
        self.sprite_sheet = SpriteSheetGrid(self.player_img, 3, 4, color_key=None, has_alpha=True)
        self.image = self.sprite_sheet.get_image(0)
        self.rect = self.image.get_rect()
        self.move_rect(self.position)

    def update(self):
        self.read_controls()
        super().update()
        if self.is_moving:
            ticks = pygame.time.get_ticks() - self.started_moving
            diff = min(ticks / self.millis_per_grid_sq, 1.0)
            anim = 0 if diff < 0.5 else 2
        else:
            anim = 1
        if self.facing == 'up':
            self.image = self.sprite_sheet.get_image((anim, 3))
        elif self.facing == 'down':
            self.image = self.sprite_sheet.get_image((anim, 0))
        elif self.facing == 'left':
            self.image = self.sprite_sheet.get_image((anim, 1))
        elif self.facing == 'right':
            self.image = self.sprite_sheet.get_image((anim, 2))


    def read_controls(self):
        if not self.is_moving:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.image = self.sprite_sheet.get_image(0)
                self.start_moving('down')
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.image = self.sprite_sheet.get_image(1)
                self.start_moving('up')
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.image = self.sprite_sheet.get_image(2)
                self.start_moving('left')
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.image = self.sprite_sheet.get_image(3)
                self.start_moving('right')


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, *groups):
        super().__init__(groups)
        ts = game.tile_size
        self.rect = pygame.Rect(x * ts, y * ts, ts, ts)


def _test_collision(one, two):
    r = pygame.Rect(
        one.current_move.x * one.game.tile_size,
        one.current_move.y * one.game.tile_size,
        one.game.tile_size, one.game.tile_size
    )
    return r.colliderect(two.rect)
