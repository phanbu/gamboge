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
    def __init__(self, game, map, x, y, *groups):
        super().__init__(groups)
        self.game = game
        self.current_move = self.position = Vector(x, y)
        self.facing = 'down'
        self.is_moving = False
        self.move_anim = 'stop'
        self.started_moving = None
        self.millis_per_grid_sq = 100
        self.rect = None
        self.footstep = pygame.mixer.Sound("./sfx/footstep.wav")

    def start_moving(self, direction):
        if not self.is_moving:
            self.started_moving = pygame.time.get_ticks()
            self.facing = direction
            self.current_move = self.position + DIRECTIONS[self.facing]
            if pygame.sprite.spritecollide(self, self.game.obstacles, False, test_for_collision):
                self.current_move = self.position
                self.is_moving = False
            else:
                self.footstep.play()
                self.is_moving = True

    def update(self):
        super().update()
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
        self.player_img = path.join(path.dirname(__file__), 'images', 'p017.png')
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
            # see if I ran into an exit
            print(self.game.state)
            # if pygame.sprite.spritecollide(Player, exits, False):
            #     print('next_state')
            # if I did, print the new coordinates

            # then move the player and load the new map
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
            if keys[pygame.K_SPACE]:
                s = pygame.sprite.spritecollideany(self, self.game.interacts, nearby)
                if s: s.interact()


class NPC(Character):
    def __init__(self, game, name, x, y, img, *groups):
        super().__init__(game, x, y, groups)
        self.name = name
        self.img_file = path.join(path.dirname(__file__), 'images', img + '.png')
        self.sprite_sheet = SpriteSheetGrid(self.img_file, 3, 4, color_key=None, has_alpha=True)
        self.image = self.sprite_sheet.get_image(1)
        self.rect = self.image.get_rect()
        self.move_rect(self.position)
        self.message = "Bob:  Hey! You can't leave town yet."

    def interact(self):
        if self.message is not None:
            self.game.messages.set_message(self.message)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, map, x, y, *groups):
        super().__init__(groups)
        ts = map.tile_size
        self.rect = pygame.Rect(x * ts, y * ts, ts, ts)


class MessageBox(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(groups)
        s = pygame.display.get_surface()
        self.image = pygame.Surface((s.get_width(), int(s.get_height() * 1/10))).convert()
        self.rect = pygame.Rect((0, s.get_height() * 9/10), self.image.get_size())
        self.text = None
        self.ticks = None
        self.set_message('Hello!')

    def set_message(self, msg):
        self.image.set_alpha(200)
        self.image.fill(0)
        f = pygame.font.SysFont('Ariel', 20)
        surface = f.render(msg, True, (255,255,255))
        self.image.blit(surface, (5,5))
        self.ticks = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.ticks > 2_000:
            self.image.set_alpha(0)


def test_for_collision(one, two):
    r = pygame.Rect(
        one.current_move.x * one.game.tile_size,
        one.current_move.y * one.game.tile_size,
        one.game.tile_size, one.game.tile_size
    )
    return r.colliderect(two.rect)

def nearby(one, two):
    ts = one.game.tile_size
    r = pygame.Rect(
        one.position.x * ts - ts,
        one.position.y * ts - ts,
        3*ts, 3*ts
    )
    return r.colliderect(two.rect)

