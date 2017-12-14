import pygame
import os, sys

HORIZONTAL = 0
VERTICAL = 1


class SpriteSheet:
    """ Class used to retrieve individual images from a sprite sheet. """

    def __init__(self, img, color_key=-1, has_alpha=False):
        """ Loads a sprite sheet from `filename` """
        try:
            img = _convert_to_pygame_surface(img)
            self.sheet = img.convert_alpha() if has_alpha else img.convert()
        except pygame.error as error:
            print("Unable to load sprite sheet file: ", str(img), file=sys.stderr)
            raise
        self.color_key = color_key
        self.has_alpha = has_alpha
        self.cache = {}

    def get_image(self, rect):
        """ Gets the image in `rect` from the sprite sheet """
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect)
        key = str(rect)
        if key in self.cache:
            result = self.cache[key]
        else:
            result = _extract_sprite_image(self.sheet, rect, self.color_key, self.has_alpha)
            self.cache[key] = result
        return result

    def get_image_list(self, *rects):
        result = []
        for r in rects:
            result.append(self.get_image(r))
        return result


class SpriteSheetGrid(SpriteSheet):
    """ A sprite sheet with a grid of images """
    def __init__(self, img, num_columns, num_rows, color_key=-1, has_alpha=False):
        super().__init__(img, color_key, has_alpha)
        self.rows = num_rows
        self.cols = num_columns
        self.img_width = self.sheet.get_width() // num_columns
        self.img_height = self.sheet.get_height() // num_rows

    def get_image(self, rect):
        result = None
        if (isinstance(rect, (list, tuple)) and len(rect) == 4) \
        or (isinstance(rect, pygame.Rect)):
            result = super().get_image(rect)
        elif isinstance(rect, (list, tuple)) and len(rect) == 2:
            x = (rect[0] % self.cols) * self.img_width
            y = (rect[1] % self.rows) * self.img_height
            result = super().get_image((x, y, self.img_width, self.img_height))
        elif isinstance(rect, int):
            rect %= self.cols * self.rows
            x = (rect % self.cols) * self.img_width
            y = (rect // self.cols) * self.img_height
            result = super().get_image((x, y, self.img_width, self.img_height))
        else:
            raise Exception("unknown coordinate", rect)
        return result

    def get_image_list(self, *rects):
        result = []
        if len(rects) == 0:
            for r in range(self.rows):
                for c in range(self.cols):
                    result.append(self.get_image((c, r)))
        else:
            for c in rects:
                result.append(self.get_image(c))
        return result


class SpriteSheetStrip(SpriteSheetGrid):
    """ A sprite sheet where images are all in a strip """
    def __init__(self, img, num_images, direction=HORIZONTAL, color_key=-1, has_alpha=False):
        if direction == HORIZONTAL:
            super().__init__(img, num_images, 1, color_key, has_alpha)
        elif direction == VERTICAL:
            super().__init__(img, 1, num_images, color_key, has_alpha)
        else:
            raise Exception("SpriteSheetStrip constructor: invalid direction: " + direction)


def _convert_to_pygame_surface(obj) -> pygame.Surface:
    if isinstance(obj, pygame.Surface):
        return obj
    elif isinstance(obj, str):
        if os.path.isfile(obj):
            return pygame.image.load(obj)
    raise ValueError("could not create surface: {}".format(str(obj)), obj)


def _extract_sprite_image(sheet, rect, color_key, has_alpha):
    img = pygame.Surface(rect.size, pygame.SRCALPHA, 32)
    img = img.convert_alpha() if has_alpha else img.convert()
    img.blit(sheet, (0, 0), rect)
    if color_key == -1:
        img.set_colorkey(img.get_at((0, 0)))
    else:
        img.set_colorkey(color_key)
    return img