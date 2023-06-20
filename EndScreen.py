import _common as common
from _prepare import *
import pygame


class EndScreen(common.State):
    def __init__(self):
        common.State.__init__(self)

        self.background = pygame.transform.scale(pygame.image.load("images/greathall.jpg").convert(), RESOLUTION)
        self.result = None
        self.players_stats = None
        self.villains_order = None
        self.buttons = []

    def startup(self):
        self.result = common.State.gamestats['result']
        self.players_stats = common.State.gamestats['players']
        self.villains_order = common.State.gamestats['villains_order']
        self.buttons.append(common.Button((840, 600), "Retourner au menu principal", self.mainmenu))

    def mainmenu(self):
        self.next = "MainMenu"
        self.done = True

    def draw(self, screen):
        screen.blit(self.background, (0,0))
        if self.result:
            txt = ENCHANTED[118].render("Game Over", True, 'black')
            screen.blit(txt, ((RESOLUTION[0]-txt.get_width())/2, 200))
        else:
            txt = ENCHANTED[118].render("Victoire !", True, 'black')
            screen.blit(txt, ((RESOLUTION[0]-txt.get_width())/2, 200))
        for b in self.buttons:
            screen.blit(b.image, b.rect)
