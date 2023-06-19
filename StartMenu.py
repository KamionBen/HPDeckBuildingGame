import pygame.draw
import _common as common
from _prepare import *
from pygame.locals import *
from core import *


class StartMenu(common.State):
    def __init__(self):
        common.State.__init__(self)
        self.buttons = []
        self.characters = {'Harry Potter': 0, 'Hermione Granger': 0, 'Ron Weasley': 0, 'Neville Londubat': 0}
        self.chosen_year = 1

        self.background = pygame.transform.scale(
            pygame.image.load("images/poudlardexpress/poudlardexpress_00000.png").convert_alpha(), RESOLUTION)

        self.title = pygame.Surface((RESOLUTION[0], 400), SRCALPHA, 32)

    def startup(self):
        """ startup"""

        """ TITLE """
        title = ENCHANTED[100].render("Harry Potter Deck Building Game", True, 'black')
        version = AQUIFER[32].render(f"Version {VERSION}", True, 'black')
        self.title.blit(title, ((self.title.get_width() - title.get_width()) / 2, 100))
        self.title.blit(version, ((self.title.get_width() - version.get_width()) / 2, 260))

        """ YEAR BUTTONS """
        years = {i + 1: False for i in range(7)}
        years[self.chosen_year] = True
        n = 0
        for y, s in years.items():
            if s:
                color = 'white'
            else:
                color = (80, 80, 80)

            position = (200 + n * 220, 400)
            size = (200, 50)
            if y == 1:
                func = self.select_year
            else:
                func = None

            b = common.Button(position, f"Année {y}", function=func, size=size, font_color=color, param={'year': y})
            self.buttons.append(b)
            n += 1

        """ PLAYERS BUTTONS """
        states = ["Off", "Player", "Dumbest AI"]

        i = 0
        for name, state in self.characters.items():
            size = (400, 50)
            position = (140 + 420 * i, 500)

            """ CHARACTER """
            n = common.Button(position, name, None, size=size)
            self.buttons.append(n)

            """ SWITCH BUTTON """
            b = common.Button((position[0] + 100, position[1] + 55), states[state], function=self.change_char_status, param={'char': name}, target=name)
            self.buttons.append(b)
            i += 1

        """ START GAME """
        button = common.Button((860, 800), "Commencer", None, font_color='grey')
        self.buttons.append(button)

    def start_game(self):
        characters = [Character(c) for c, s in self.characters.items() if s == 1]
        common.State.gamedata = {'characters': characters, 'year': self.chosen_year}

        self.next = "GameScreen"
        self.previous = "StartMenu"
        self.done = True

    def change_char_status(self, char: str):
        states = ["Off", "Player", "Dumbest AI"]
        new_value = (self.characters[char] + 1) % 3
        self.characters[char] = new_value
        for button in self.buttons:
            if button.target == char:
                button.text = states[new_value]
                button.update()

    def update(self):
        players_ready = 0
        for status in self.characters.values():
            if status == 1:
                players_ready += 1
        for button in self.buttons:
            if button.text.split(" ")[0] == "Année":
                if int(button.text.split(" ")[1]) == self.chosen_year:
                    button.font_color = 'white'
                else:
                    button.font_color = (80, 80, 80)
            if button.text == "Commencer":
                if players_ready >= 2:
                    button.function = self.start_game
                    button.font_color = "green"
                else:
                    button.function = None
                    button.font_color = "gray"
            button.update()

    def get_event(self, event):
        if event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        if button.function is not None:
                            if button.param is None:
                                button.function()
                            else:
                                button.function(**button.param)
                            #self.update()


    def select_year(self, year):
        self.chosen_year = year

    def draw(self, screen):
        screen.fill('black')
        screen.blit(self.background, (0,0))
        screen.blit(self.title, ((RESOLUTION[0] - self.title.get_width()) / 2, 0))

        for b in self.buttons:
            screen.blit(b.image, b.rect)

