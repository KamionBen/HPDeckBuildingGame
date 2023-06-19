import pygame as pg
from _prepare import *


class State:
    gamedata = {}
    gamestats = {}

    def __init__(self):
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None

    def update(self):
        """ Do things every tick """

    def draw(self, screen):
        """ Draw stuff on screen """

    def startup(self):
        """ Do things when the State start """

    def cleanup(self):
        """ Do things when the State end """

    def get_event(self, event):
        """ Catch events """

    def validate(self):
        """ Enter, or cross button """
        pass

    def cancel(self):
        """ Backspace or circle """
        pass


class Button(pg.sprite.Sprite):
    def __init__(self, position: (int, int), text: str = "", function=None, size: (int, int) = (200, 50), param=None,
                 bg_color=(40, 40, 40), font_size=28, font_color="white", target=None):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size).convert_alpha()
        self.rect = self.image.get_rect()
        self.position = position
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.function = function
        self.param = param
        self.target = target

        self.update()

    def update(self):
        self.image.fill(self.bg_color)
        r_text = AQUIFER[self.font_size].render(self.text, True, self.font_color)
        self.image.blit(r_text,
                        ((self.rect.width - r_text.get_width()) / 2, (self.rect.height - r_text.get_height()) / 2))




