import pygame


class Music:
    def __init__(self, screen):
        super().__init__()
        self.direction = 1
        self.speed = 10
        self.screen = screen
        self.sound = pygame.mixer.Sound("./resources/sounds/fireball.wav")
        self.fireball = pygame.image.load("./resources/pics/fireball.png").convert()
        self.image = self.fireball
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect()
        self.rect.topright = (-200, 20)

    def update(self):
        super().update()
        if self.rect.left > self.screen.get_width() + 450:
            self.direction = -1
            self.speed = 5
            self.rect.left = self.screen.get_width()
            self.rect.top = self.screen.get_height() * 1/3
            self.image = pygame.transform.flip(self.fireball, True, False)
            self.image = pygame.transform.smoothscale(self.image, (102, 50))
            self.image.set_colorkey(self.image.get_at((0, 0)))
        elif self.rect.right < 0:
            self.direction = 1
            self.speed = 15
            self.rect.right = 0
            self.rect.centery = self.screen.get_height()/2
            self.image = self.fireball;
            self.sound.play()

        self.rect = self.rect.move(self.direction * self.speed, 0)

    def draw(self):
        self.screen.blit(self.image, self.rect)


def play():
    pygame.init()
    pygame.mixer.music.load("./sfx/piano-loop.wav")
    pygame.mixer.music.play(-1)
    screen = pygame.display.set_mode((1530, 300))
    space = pygame.image.load("./resources/pics/space.png").convert()
    space.set_colorkey(space.get_at((0,0)))
    fireball = Music(screen)
    finished = False
    clock = pygame.time.Clock()

    while not finished:
        for e in pygame.event.get():
            if e.type == pygame.QUIT \
            or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                finished = True

        screen.fill(0)
        fireball.update()

        if fireball.direction > 0:
            screen.blit(space, (0,0))
            fireball.draw()
        else:
            fireball.draw()
            screen.blit(space, (0,0))

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    play()
