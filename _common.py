import pygame as pg
from pygame.constants import *
from _prepare import *


class State:
    gamedata = {}
    gamestats = {}

    def __init__(self):
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None

        self.buttons = []

    def update(self):
        """ Do things every tick """

    def draw(self, screen):
        """ Draw stuff on screen """

    def startup(self):
        """ Do things when the State start """

    def cleanup(self):
        """ Do things when the State end """

    def get_event(self, event):
        if event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos) and button.function is not None:
                        if button.param is None:
                            button.function()
                        else:
                            button.function(**button.param)

    def validate(self):
        """ Enter, or cross button """
        pass

    def cancel(self):
        """ Backspace or circle """
        pass

ratio = 1
if RESOLUTION[0] == 1280:
    ratio = 0.66

class Button(pg.sprite.Sprite):
    def __init__(self, position: (int, int), text: str = "", function=None, size: (int, int) = (200, 50), param=None,
                 bg_color=(40, 40, 40), font_size=28, font_color="white", target=None):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((size[0] * ratio, size[1] * ratio)).convert_alpha()
        self.rect = self.image.get_rect()
        self.position = position[0] * ratio, position[1] * ratio
        self.rect.x = position[0] * ratio
        self.rect.y = position[1] * ratio
        self.text = text
        self.font_size = int(font_size * ratio)
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




