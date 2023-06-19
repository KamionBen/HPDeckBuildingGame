import json
from random import shuffle
import pygame
from pygame.locals import SRCALPHA
from _prepare import *
from os import path

""" MOTHER CLASSES """

class Card(pygame.sprite.Sprite):
    def __init__(self, name: str, year: int):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.year = year

    def __repr__(self):
        return self.name


class Deck(pygame.sprite.Group):
    def __init__(self, *cards):
        pygame.sprite.Group.__init__(self)
        self._cards = [c for c in cards]

    def append(self, card):
        self._cards.append(card)

    def get(self, item):
        for elt in self._cards:
            if elt == item:
                return elt

    def shuffle(self):
        shuffle(self._cards)

    def copy(self):
        return [e for e in self._cards]

    def pick(self) -> Card:
        return self._cards.pop(0)

    def remove(self, card):
        self._cards.remove(card)

    def __iter__(self):
        return iter(self._cards)

    def __repr__(self):
        return str(self._cards)

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, index):
        return self._cards[index]

    def insert(self, index, item):
        self._cards.insert(index, item)

class OrderedDeck:
    def __init__(self):
        """ Represent and manage de 6 Hogwarts cards """
        self._cards = [None for _ in range(6)]

    def get_vacant(self):
        vacant = 0
        for elt in self._cards:
            if elt is None:
                vacant += 1
        return vacant

    def add(self, newcard: Card):
        if self.get_vacant() == 0:
            raise IndexError
        else:
            for i, card in enumerate(self._cards):
                if card is None:
                    self._cards[i] = newcard
                    break

    def remove(self, rm_card):
        found = False
        for i, card in enumerate(self._cards):
            if card == rm_card:
                self._cards[i] = None
                found = True

        if not found:
            raise IndexError(f"{rm_card} n'a pas été trouvée")

    def __len__(self):
        return 6-self.get_vacant()

    def __iter__(self):
        return iter(self._cards)




""" DAUGHTER CLASSES """

location_dict = {"Chemin de Traverse": pygame.image.load('images/diagon_alley.png').convert(),
                 "Miroir du Risèd": pygame.image.load('images/miroir_du_rised.png').convert()}

MARK = pygame.image.load('images/marque.png').convert_alpha()

class Location(Card):
    def __init__(self, year, order, name, events_nb, control_nb):
        Card.__init__(self, name, year)
        self.order = order

        self.event_nb = events_nb
        self.control_nb, self.control_nb_max = 0, control_nb

        self.image = pygame.Surface((1200, 150))
        self.rect = self.image.get_rect()
        # Card size : 10.2 / 7.6 (ratio : 1.34)

        self.update()

    def update(self):
        self.image.blit(location_dict[self.name], (0,0))

        """ NB EVENTS """
        nb_event = AQUIFER[18].render(f"Révélez {self.event_nb} évènement Forces du Mal", True, 'grey')
        self.image.blit(nb_event, (10, 10))

        """ LIEU """
        lieu = AQUIFER[24].render("LIEU", True, 'yellow')
        self.image.blit(lieu, (10, 50))

        """ NAME """
        text = ENCHANTED[60].render(self.name, True, 'white')
        self.image.blit(text, (10, 70))

        """ TOKENS """
        for i in range(self.control_nb_max):
            position = (600 + i * 50, 100 + (i % 2 * 10))
            if self.control_nb > i:
                self.image.blit(MARK, position)
            else:
                mark = pygame.transform.grayscale(MARK)
                mark.set_alpha(128)
                self.image.blit(mark, position)


        #control = FONT[28].render(f"{self.control_nb}/{self.control_nb_max}", True, 'white')
        #self.image.blit(control, ((self.rect.width-control.get_width())/2, 200))

    def is_dead(self):
        return self.control_nb == self.control_nb_max

    def add_token(self, nb=1):
        self.control_nb = min(self.control_nb + nb, self.control_nb_max)

TOKEN = pygame.image.load("images/attack.png").convert_alpha()


class Villain(Card):
    def __init__(self, year, name, health, description, reward, mechanics):
        Card.__init__(self, name, year)
        self.description = description
        self.reward = reward

        self.health, self.health_max = 0, health
        self.mechanics = mechanics
        self.attack_tokens = 0
        self.image = pygame.Surface((306, 228))
        self.rect = self.image.get_rect()

    def update(self):

        """ FRAME """
        self.image.fill('black')
        pygame.draw.rect(self.image, (40, 40, 40), (1, 1, self.rect.width-2, self.rect.height-2), border_radius=5)

        subtext = AQUIFER[20].render("ENNEMI", True, 'yellow')
        self.image.blit(subtext, (10, 10))

        text = ENCHANTED[48].render(self.name, True, 'white')
        self.image.blit(text, (10, 30))

        for i in range(self.health_max):
            position = (5 + i * 45, 80 + (i%2 * 10))
            if self.health + self.attack_tokens < i + 1:
                token = pygame.transform.grayscale(TOKEN)
                token.set_alpha(128)
                self.image.blit(token, position)
            else:

                self.image.blit(TOKEN, position)

        #health = FONT[28].render(f"{self.health}/{self.health_max}", True, 'white')
        #self.image.blit(health, (250, 10))

        #tokens = FONT[20].render(f"Attack tokens : {self.attack_tokens}", True, 'white')
        #self.image.blit(tokens, (140, 120))

        #description = FONT[22].render(self.description, True, 'grey')
        #self.image.blit(description, (5, 100))

        #reward = FONT[22].render(self.reward, True, 'grey')
        #self.image.blit(reward, (5, 150))

    def assign_token(self, nb):
        self.attack_tokens += nb

    def is_dead(self):
        return self.health + self.attack_tokens >= self.health_max

    def endturn(self):
        self.health += self.attack_tokens
        self.attack_tokens = 0

    def heal(self, nb):
        self.health = max(self.health - nb, self.health)


class DarkArts(Card):
    def __init__(self, year, name, description, mechanics):
        Card.__init__(self, name, year)
        self.description = description
        self.mechanics = mechanics

        self.image = pygame.Surface((228, 228))
        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill('black')
        pygame.draw.rect(self.image, (40,40,40), (1,1,self.rect.width-2,self.rect.height-2), border_radius=5)
        text = AQUIFER[24].render(self.name, True, 'white')
        self.image.blit(text, (10,10))

        limit = 25
        phrase_ls = []
        string = ""
        for word in self.description.split(" "):
            if len(string + " " + word) < limit:
                string = string + " " + word
            else:
                phrase_ls.append(string)
                string = word
        phrase_ls.append(string)
        for i, phrase in enumerate(phrase_ls):
            description = FONT[20].render(phrase, True, 'white')
            self.image.blit(description, ((self.rect.width - description.get_width()) / 2, 70 + i * 20))


class Hogwarts(Card):
    def __init__(self, year, name, description, genre, cost, mechanics):
        Card.__init__(self, name, year)
        self.description = description
        self.genre = genre
        self.cost = cost
        self.mechanics = mechanics

        # Card size : 6.3 / 8.7
        self.image = pygame.Surface((189, 261), SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.active = False

    def update(self):
        """"""
        """ FRAME """
        pygame.draw.rect(self.image, (40, 40, 40), (1, 1, self.rect.width - 2, self.rect.height - 2), border_radius=5)
        pygame.draw.rect(self.image, 'grey', (1, 1, self.rect.width - 2, self.rect.height - 2), border_radius=5, width=2)

        """ GENRE """
        posy = 10
        genre_colors = {'objet': YELLOW, 'sort': RED, 'allié': BLUE}
        genre = AQUIFER[16].render(self.genre.upper(), True, 'white')
        pygame.draw.rect(self.image, genre_colors[self.genre], (10, posy, self.rect.width - 20, 20))
        self.image.blit(genre, ((self.rect.width - genre.get_width()) / 2, posy + 2))

        """ TITLE """
        posy = 50
        text = AQUIFER[16].render(self.name.upper(), True, 'white')
        self.image.blit(text, ((self.rect.width-text.get_width())/2, posy))

        """ DESCRIPTION """
        posy = 100
        limit = 25
        phrase_ls = []
        string = ""
        #description = self.description.replace("!coeur", "♥️")
        for word in self.description.split(" "):
            if len(string + " " + word) < limit:
                string = string + " " + word
            else:
                phrase_ls.append(string)
                string = word
        phrase_ls.append(string)
        for i, phrase in enumerate(phrase_ls):
            description = FONT[20].render(phrase, True, 'white')
            self.image.blit(description, ((self.rect.width - description.get_width()) / 2, posy + i * 20))

        """ COST """
        if self.active:
            cost_color = 'green'
        else:
            cost_color = 'white'
        posy = 230
        cost = AQUIFER[28].render(str(self.cost), True, cost_color)
        self.image.blit(cost, (150, posy))






""" IMPORT FUNCTIONS """

CARD_DIR = "cards"
# CARD_DIR = "cards"


def import_locations(year) -> Deck:
    with open(path.join(CARD_DIR, 'locations.json'), 'r', encoding='utf-8') as deck_file:
        data = json.load(deck_file)
    deck = Deck(*[Location(**c) for c in data if c['year'] == year])
    return deck


def import_darkarts(year) -> Deck:
    with open(path.join(CARD_DIR, 'darkarts.json'), 'r', encoding='utf-8') as deck_file:
        data = json.load(deck_file)
    deck = []
    for card in data:
        if card['year'] <= year:
            nb = card['nb']
            card.pop('nb')
            for i in range(nb):
                deck.append(card)
    deck = Deck(*[DarkArts(**c) for c in deck])
    deck.shuffle()
    return deck


def import_hogwarts(year) -> Deck:
    with open(path.join(CARD_DIR, 'hogwarts.json'), 'r', encoding='utf-8') as deck_file:
        data = json.load(deck_file)
    deck = []
    for card in data:
        if card['year'] <= year:
            nb = card['nb']
            card.pop('nb')
            for i in range(nb):
                deck.append(card)
    deck = Deck(*[Hogwarts(**c) for c in deck])
    deck.shuffle()
    return deck


def import_villains(year) -> Deck:
    with open(path.join(CARD_DIR, 'villains.json'), 'r', encoding='utf-8') as deck_file:
        data = json.load(deck_file)
    deck = Deck(*[Villain(**c) for c in data if c['year'] <= year])
    deck.shuffle()
    return deck


def import_basedeck(character) -> Deck:
    with open(path.join(CARD_DIR, 'basedecks.json'), 'r', encoding='utf-8') as deck_file:
        data = json.load(deck_file)

    deck = []
    for card in data:
        if card['character'] == character:
            nb = card.pop('nb')
            card.pop('character')
            for i in range(nb):
                deck.append(card)
    deck = Deck(*[Hogwarts(**c) for c in deck])
    deck.shuffle()
    if len(deck) == 10:
        return deck
    else:
        raise ValueError(f"Le deck ne contient pas 10 cartes mais {len(deck)}")


class Recto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((189, 261), SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.logo = pygame.image.load('images/blason.png').convert_alpha()
        self.update()

    def update(self):
        """ FRAME """
        pygame.draw.rect(self.image, (40, 40, 40), (1, 1, self.rect.width - 2, self.rect.height - 2), border_radius=5)
        pygame.draw.rect(self.image, 'grey', (1, 1, self.rect.width - 2, self.rect.height - 2), border_radius=5,
                         width=2)
        logo = pygame.transform.grayscale(self.logo)
        logo = pygame.transform.scale(logo, (100, 100))
        logo.set_alpha(50)
        self.image.blit(logo, ((189-100)/2, (261-100)/2))


if __name__ == '__main__':
    pass