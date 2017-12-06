import pygame
import sys

HORIZONTAL = 0
VERTICAL = 1


class SpriteSheet:
    """ Class used to retrieve individual images from a sprite sheet. """

    def __init__(self, img, color_key=-1, has_alpha=False):
        """ Loads a sprite sheet from `filename` """
        try:
            img = pygame.image.load(img)
            self.sheet = img.convert_alpha() if has_alpha else img.convert()
        except pygame.error as error:
            print("Unable to load sprite sheet file: ", str(img), file=sys.stderr)
            raise
        self.color_key = color_key
        self.has_alpha = has_alpha

    def get_image(self, rect):
        """ Gets the image in `rectangle` from the sprite sheet """
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect)
        if self.has_alpha:
            img = pygame.Surface(rect.size, pygame.SRCALPHA, 32)
            img.convert_alpha()
        else:
            img = pygame.Surface(rect.size)
            img = img.convert_alpha() if self.has_alpha else img.convert()
        img.blit(self.sheet, (0, 0), rect)
        if self.color_key is not None:
            if self.has_alpha:
                img.set_colorkey((0,0,0))
            elif self.color_key == -1:
                img.set_colorkey(img.get_at((0, 0)))
            else:
                img.set_colorkey(self.color_key)
        return img

    def get_image_list(self, *coords):
        result = []
        for r in coords:
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

    def get_image(self, coord):
        result = None
        if (isinstance(coord, (list,tuple)) and len(coord) == 4) \
        or (isinstance(coord, pygame.Rect)):
            result = super().get_image(coord)
        elif isinstance(coord, (list,tuple)) and len(coord) == 2:
            x = (coord[0] % self.cols) * self.img_width
            y = (coord[1] % self.rows) * self.img_height
            result = super().get_image((x, y, self.img_width, self.img_height))
        elif isinstance(coord, int):
            coord %= self.cols * self.rows
            x = (coord % self.cols) * self.img_width
            y = (coord // self.cols) * self.img_height
            result = super().get_image((x, y, self.img_width, self.img_height))
        else:
            raise Exception("unknown coordinate", coord)
        return result

    def get_image_list(self, *coords):
        result = []
        if len(coords) == 0:
            for r in range(self.rows):
                for c in range(self.cols):
                    result.append(self.get_image((c, r)))
        else:
            for c in coords:
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
