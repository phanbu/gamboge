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
    def __init__(self, game, position, *groups):
        super().__init__(groups)
        self.game = game
        self.tile_size = game.tile_size
        self.current_move = self.position = position
        self.facing = 'down'
        self.is_moving = False
        self.move_anim = 'stop'
        self.started_moving = None
        self.millis_per_grid_sq = 200
        self.rect = None
        self.footstep = pygame.mixer.Sound("./sfx/footstep.wav")

    def start_moving(self, direction):
        if not self.is_moving:
            self.started_moving = pygame.time.get_ticks()
            self.facing = direction
            self.current_move = self.position + DIRECTIONS[self.facing]
            if pygame.sprite.spritecollide(self, self.game.state.map.obstacles, False, test_for_collision):
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
                self.move_rect(self.current_move)
                self.is_moving = False


    def move_rect(self, position, distance=Vector(0, 0)):
        if distance.x==0 and distance.y==0:
            self.position = self.current_move = position
        loc = Vector((position.x + distance.x) * self.tile_size.x , (position.y + distance.y + 1) * self.tile_size.y)
        self.rect.bottomleft = (loc.x, loc.y)


class Player(Character):
    def __init__(self, game, position, *groups):
        super().__init__(game, position, groups)
        self.player_img = path.join(path.dirname(__file__), 'images', 'p017.png')
        self.sprite_sheet = SpriteSheetGrid(self.player_img, 3, 4, color_key=None, has_alpha=True)
        self.image = self.sprite_sheet.get_image(0)
        self.rect = self.image.get_rect()
        self.move_rect(self.position)

    def update(self):
        self.read_controls()
        was_moving = self.is_moving
        super().update()

        if self.is_moving:
            ticks = pygame.time.get_ticks() - self.started_moving
            diff = min(ticks / self.millis_per_grid_sq, 1.0)
            anim = 0 if diff < 0.5 else 2
        else:
            anim = 1

        if was_moving and not self.is_moving:
            exit = pygame.sprite.spritecollideany(self, self.game.state.map.exits)
            if exit:
                print(exit.next_state, exit.player_position)
                self.game.change_state(self.game.states[exit.next_state])
                self.move_rect(exit.player_position)

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
                s = pygame.sprite.spritecollideany(self, self.game.state.map.interacts, nearby)
                if s: s.interact()


class NPC(Character):
    def __init__(self, game, name, position, img, *groups):
        super().__init__(game, position, groups)
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
    def __init__(self, game, position, *groups):
        super().__init__(groups)
        ts = game.tile_size
        self.rect = pygame.Rect(position.x * ts.x, position.y * ts.y, ts.x, ts.y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, rect, next_state, player_position, *groups):
        super().__init__(groups)
        self.rect = rect
        self.next_state = next_state
        self.player_position = player_position


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
        one.current_move.x * one.game.tile_size.x,
        one.current_move.y * one.game.tile_size.y,
        one.game.tile_size.x, one.game.tile_size.y
    )
    return r.colliderect(two.rect)


def nearby(one, two):
    ts = one.game.tile_size
    r = pygame.Rect(
        one.position.x * ts.x - ts.x,
        one.position.y * ts.y - ts.y,
        3*ts.x, 3*ts.y
    )
    return r.colliderect(two.rect)

