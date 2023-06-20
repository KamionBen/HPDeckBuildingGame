import pygame
from pygame.constants import *
import _common as common
from _prepare import *


class Configuration(common.State):
    def __init__(self):
        common.State.__init__(self)
        self.buttons = []

        self.background = None
        self.title = None

        self.options = {"Resolution": [(1920, 1080), (1280, 720)],
                        "Langage": ["Français"]}
        self.selection = {name: 0 for name in self.options.keys()}

    def startup(self):
        self.background = pygame.transform.scale(MAIN_BACKGROUND, RESOLUTION)
        self.title = pygame.Surface((RESOLUTION[0], 400), SRCALPHA, 32)
        title = ENCHANTED[100].render("Harry Potter Deck Building Game", True, 'black')
        version = AQUIFER[32].render(f"Version {VERSION}", True, 'black')
        self.title.blit(title, ((self.title.get_width() - title.get_width()) / 2, 100))
        self.title.blit(version, ((self.title.get_width() - version.get_width()) / 2, 260))
        self.update_buttons()

    def update_buttons(self):
        self.buttons = []
        i = 0
        posx, posy = 560, 600
        span = 50
        for config, options in self.options.items():
            b = common.Button((posx, posy + i * span), config)
            self.buttons.append(b)
            i += 1

            position = posx, posy + i * span
            s = self.selection[config]
            b = common.Button(position, str(options[s]), self.change_selection, param={'config':config})
            self.buttons.append(b)
            i += 1

    def change_selection(self, config):
        new_value = self.selection[config] + 1
        if new_value >= len(self.options[config]):
            new_value = 0
        self.selection[config] = new_value
        self.update_buttons()

    def draw(self, screen):
        screen.blit(self.background, (0,0))
        screen.blit(self.title, (0,0))
        for b in self.buttons:
            screen.blit(b.image, b.rect)
