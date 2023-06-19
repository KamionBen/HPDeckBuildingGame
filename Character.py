from Cards import *


class Profile:
    def __init__(self, name, **kw):
        self.name = name
        for k, v in kw.items():
            self.__setattr__(k, v)


HEART = pygame.transform.scale(pygame.image.load("images/tokens/heart.png").convert_alpha(), (30, 30))
ATTACK = pygame.image.load("images/tokens/attack.png").convert_alpha()
INFLUENCE = pygame.image.load("images/tokens/influence.png").convert_alpha()


class Character(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.firstname = name.split(' ')[0]

        self.deck = import_basedeck(self.name)
        self.hand = Deck()
        self.played = Deck()
        self.discard_pile = Deck()

        self.health = 10
        self.influence = 0
        self.attack = 0
        self.effects = []
        self.triggers = []

        self.stunned = False
        self.has_discarded = False

        self.image = pygame.Surface((400, 200), SRCALPHA, 32)
        self.rect = self.image.get_rect()

        self.active = False
        self.update()
        self.update_image()


    def update_image(self):
        """"""
        sizes = {True: (400, 200), False: (150, 200)}
        width, height = sizes[self.active]
        self.image = pygame.Surface((width, height), SRCALPHA, 32)
        """ FRAME """
        self.image.fill('white')
        pygame.draw.rect(self.image, (40,40,40), (1,1, width-2, height-2))

        if self.active:
            """ NAME """
            name = ENCHANTED[44].render(self.name, True, 'white')
            self.image.blit(name, ((400-name.get_width())/2, 0))
            """ IMG HEALTH """
            for i in range(10):
                position = (25 + i * 35, 60 + (i%2*10))
                if self.health > i:
                    self.image.blit(HEART, position)
                else:
                    self.image.blit(pygame.transform.grayscale(HEART), position)

            """ INFLUENCE """
            if self.influence > 0:
                self.image.blit(INFLUENCE, (280, 140))
                txt = AQUIFER[32].render(f"x {self.influence}", True, 'white')
                self.image.blit(txt, (330, 145))
            #influence = FONT[32].render(f"Influence : {self.influence}", True, 'white')
            #self.image.blit(influence, (220, 150))

            """ ATTACK """
            if self.attack > 0:
                x, y = 10, 140
                self.image.blit(ATTACK, (x, y))
                txt = AQUIFER[32].render(f"x {self.attack}", True, 'white')
                self.image.blit(txt, (x + 50, y + 5))

            #attack = FONT[32].render(f"Attack : {self.attack}", True, 'white')
            #self.image.blit(attack, (20, 150))

        else:
            """ FIRST NAME """
            name = ENCHANTED[32].render(self.firstname, True, 'white')
            self.image.blit(name, (10, 10))

            """ TEXT HEALTH """
            health = AQUIFER[32].render(f"{self.health}/10", True, 'red')
            self.image.blit(health, (10, 40))

            """ INFLUENCE """
            influence = AQUIFER[22].render(f"Influence : {self.influence}", True, 'white')
            self.image.blit(influence, (10, 100))
            """ ATTACK """
            attack = AQUIFER[22].render(f"Attack : {self.attack}", True, 'white')
            self.image.blit(attack, (10, 120))

    def update(self):
        for card in self.hand:
            card.update()

    def heal(self, nb):
        if not self.stunned:
            self.health = min(self.health + nb, 10)

    def __repr__(self):
        return self.name

    def get_damage(self, nb):
        if not self.stunned:
            self.health -= nb

    def gain_influence(self, nb):
        self.influence += nb

    def gain_attack(self, nb):
        self.attack += nb

    def pick(self, nb):
        for _ in range(nb):
            if len(self.deck) == 0:
                self.discard_pile.shuffle()
                self.deck, self.discard_pile = self.discard_pile, Deck()
            self.hand.append(self.deck.pick())
        for card in self.hand:
            if "in_hand" in card.mechanics.keys():
                for elt in card.mechanics['in_hand']:
                    if elt not in self.effects:
                        self.effects.append(elt)

    def pick_five(self):
        self.pick(5)

    def play(self, card):
        self.hand.remove(card)
        self.played.append(card)

    def discard(self, card):
        self.hand.remove(card)
        self.discard_pile.append(card)

    def buy(self, card: Hogwarts, discard=True):
        if discard:
            self.discard_pile.append(card)
        else:
            self.deck.insert(0, card)
        self.influence -= card.cost

    def endturn(self):
        for card in self.hand:
            self.discard_pile.append(card)
        for card in self.played:
            self.discard_pile.append(card)
        self.played = Deck()
        self.hand = Deck()
        self.influence = 0
        self.attack = 0
        self.pick_five()

    def clear_effects(self):
        self.effects = []
        self.triggers = []
