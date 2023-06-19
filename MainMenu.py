import pygame.draw

import Control
import _common as common
from _prepare import *
from pygame.locals import *
from core import *
from os import scandir

class MainMenu(common.State):
    def __init__(self):
        common.State.__init__(self)
        self.buttons = []
        self.background = pygame.transform.scale(pygame.image.load("images/poudlardexpress/poudlardexpress_00000.png").convert_alpha(), RESOLUTION)

        self.title = pygame.Surface((RESOLUTION[0], 400), SRCALPHA, 32)

        self.animation_tick = 0
        self.clock = pygame.time.Clock()

    def startup(self):
        """ startup """
        """ ANIMATION """
        self.animation_tick = 0

        """ TITLE """
        title = ENCHANTED[100].render("Harry Potter Deck Building Game", True, 'black')
        version = AQUIFER[32].render(f"Version {VERSION}", True, 'black')
        self.title.blit(title, ((self.title.get_width() - title.get_width()) / 2, 100))
        self.title.blit(version, ((self.title.get_width() - version.get_width()) / 2, 260))


        """ MAIN MENU """
        menu = {"Nouvelle partie": self.start_game, "Charger une partie": None, "Quitter": self.quitter}
        i = 0
        for text, func in menu.items():
            if func is None:
                color = (80, 80, 80)
            else:
                color = 'white'

            position = ((RESOLUTION[0]-400)/2, 400 + i * 60)
            size = (400, 50)

            b = common.Button(position, text, func, size=size, bg_color=(40,40,40), font_color=color)
            self.buttons.append(b)
            i += 1

    def update(self):
        self.background.set_alpha(int(self.animation_tick / 100 * 255))
        self.title.set_alpha(int((self.animation_tick - 50) / 100 * 255))
        for i, button in enumerate(self.buttons):
            button.image.set_alpha(int((self.animation_tick - 55 + (-i * 10)) / 100 * 255))

        self.animation_tick += 1

    def draw(self, screen):
        screen.fill('black')
        screen.blit(self.background, (0,0))
        screen.blit(self.title, ((RESOLUTION[0]-self.title.get_width())/2,0))
        for b in self.buttons:
            screen.blit(b.image, b.rect)



    def get_event(self, event: pg.event.Event):
        if event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        if button.function is not None:
                            button.function()

    def start_game(self):
        self.next = "StartMenu"
        self.previous = "MainMenu"
        self.done = True

    def quitter(self):
        common.State.game_on = False
        self.quit = True

