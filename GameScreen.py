import pygame.draw
import _common as common
from _prepare import *
from pygame.locals import *
from core import *


class GameScreen(common.State):
    def __init__(self):
        common.State.__init__(self)
        self.engine = None
        self.first_player = None
        self.image = pygame.Surface(RESOLUTION)

        self.won = False
        self.next = "EndScreen"
        self.stats = {}

        self.banner_surf = pygame.Surface(RESOLUTION, SRCALPHA, 32)
        self.banner_flag = False
        self.banner_timer = 0
        self.banner_queue = []

        self.discard_flag = False
        self.dicard_panel = pygame.Surface(RESOLUTION, SRCALPHA, 32)
        self.discard_char = None
        self.discard_nb = 0
        self.discarded = []

        self.action_request = None
        self.action_value = 0
        self.choice = []

        self.temp = None

        self.buttons = []

    def startup(self):
        """ SET UP THE GAME """
        self.engine = GameEngine(common.State.gamedata['characters'], common.State.gamedata['year'])
        p_stats = {"attack_gained": 0, "attack_infliged": 0, "influence_gained": 0, "influence_spent": 0,
                   "cards_discarded": 0, "cards_bought": 0, "cards_picked": 0}
        self.stats["players"] = {p.name: {} for p in self.engine.characters}
        self.stats["villains_order"] = [v.name for v in self.engine.villains]

        for p in self.engine.characters:
            p.pick_five()
        self.engine.draw_board()
        self.engine.pick_villains()

        self._update_game()

    def cleanup(self):
        self.stats['result'] = self.engine.game_over
        common.State.gamestats = self.stats

    def update(self):
        """ RUN EACH TICK """
        if self.banner_flag:
            self.banner_timer += 1
            if self.banner_timer >= 60:  # 2 seconds
                self.banner_surf = pygame.Surface(RESOLUTION, SRCALPHA, 32)
                self.banner_flag = False
                self.banner_timer = 0
                if len(self.banner_queue) > 0:
                    self.banner(**self.banner_queue.pop(0))

    def _update_game(self):
        """ MAIN FUNCTIONS """
        if self.engine.game_over is not None:
            self.done = True
        else:
            self.buttons = []
            self.update_character()
            self.update_villains()
            self.update_board()
            self.update_location()
            if self.first_player is None:
                """ VERY FIRST ACTION """
                first = self.engine.characters[0]

                text = common.Button((700, 450), f"Commencer avec {first.firstname} ?", None,
                                          size=(520, 50))
                commencer = common.Button((800, 500), f"OUI", self.choose_first_player,
                                          size= (160, 50), param={'character': first})
                changer = common.Button((960, 500), f"NON", self.choose_first_player,
                                          size=(160, 50), param={'character': False})

                self.buttons.append(text)
                self.buttons.append(commencer)
                self.buttons.append(changer)

            elif self.action_request is not None:
                """ ACTIONS REQUESTED BY THE PLAYER """
                if self.action_request == "CHOICE":
                    if len(self.choice) > 1:

                        for i, effect in enumerate(self.choice):
                            action, nb = effect.split('_')
                            if action == "HEROHEAL":
                                for i, hero in enumerate(self.engine.characters):
                                    self.buttons.append(
                                        common.Button((900, 200 + i * 50), f"Soigner {hero.firstname} ?",
                                                      self.heroheal, param={'nb': int(nb), 'character': hero},
                                                      size=(300, 50)))
                            else:
                                self.buttons.append(common.Button((900, 400 + i * 55), effect, self.select_card,
                                                              param={'card': self.temp, 'action': effect},
                                                              size=(300, 50)))
                    else:
                        action, nb = self.choice[0].split("_")
                        if action == "HEROHEAL":
                            for i, hero in enumerate(self.engine.characters):
                                self.buttons.append(common.Button((900, 400 + i * 50), f"Soigner {hero.firstname} ?",
                                                          self.select_card, param={'card': self.temp, 'action': hero},
                                                          size=(300, 50)))

                if self.action_request == "TOPDECK":
                    for i, action in enumerate(self.choice):
                        self.buttons.append(common.Button((900, 400 + i * 50), action,
                                                          self.buy_card, param={'card': self.temp, 'topdeck': action},
                                                          size=(300, 50)))

            elif self.engine.action_request is not None:
                """ ACTIONS REQUESTED BY THE ENGINE """
                effect, nb = self.engine.action_request.split('_')

                if effect == "HEROHEAL":
                    for i, hero in enumerate(self.engine.characters):
                        self.buttons.append(common.Button((900, 400 + i * 50), f"Soigner {hero.firstname} ?",
                                                          self.heroheal, param={'nb': int(nb), 'character': hero},
                                                          size=(300, 50)))

                if effect == "DISCARDACTIVE":
                    position = (800, 300)
                    self.discard_flag = True
                    self.discard_char = self.engine.characters[0]
                    self.discard_nb = int(nb)
                    title = common.Button(position, f"Défaussez {int(nb)} carte(s)", size=(300, 50))
                    self.buttons.append(title)

                    if len(self.discarded) == self.discard_nb:
                        self.buttons.append(common.Button((900, 800), "Confirmer", self.confirm_discard,
                                                          param={'cards':self.discarded, 'villain': True}))

                if effect == "CHOICE":
                    for i, action in enumerate(self.engine.choice):
                        self.buttons.append(common.Button((900, 400 + i * 50), action,
                                                          self.select_card, param={'card': self.temp, 'action': action},
                                                          size=(300, 50)))

                if effect == "DISCARDCHAR":
                    for hero in self.engine.characters:
                        if hero.stunned:
                            position = (800, 300)
                            self.discard_flag = True
                            self.discard_char = hero
                            self.discard_nb = len(hero.hand) // 2
                            title = common.Button(position, f"Défaussez {nb} carte(s)", size=(300, 50))
                            self.buttons.append(title)

                            if len(self.discarded) == self.discard_nb:
                                self.buttons.append(common.Button((900, 800), "Confirmer", self.confirm_discard,
                                                                  param={'cards': self.discarded, 'villain': True}))





            else:
                """ CREATE CARDS BUTTONS """
                self.update_character()
                active = self.engine.characters[0]
                for i, card in enumerate(active.hand):
                    posx = (RESOLUTION[0] - (len(active.hand) * 200)) / 2
                    position = posx + i * 200, 755
                    b = common.Button(position, function=self.select_card, param={'card': card},
                                      size=(card.rect.width, card.rect.height), bg_color=(0,0,0,0))
                    self.buttons.append(b)

                """ CREATE BOARD BUTTONS """

                for i, card in enumerate(self.engine.board):
                    if card is not None:
                        """ INIT """
                        card.update()
                        if card.cost <= self.engine.characters[0].influence:
                            card.active = True
                        else:
                            card.active = False
                        position = (1300 + (i % 3 * 200), 10 + (i % 2 * 265))
                        size = (card.rect.width, card.rect.height)
                        b = common.Button(position, "", self.buy_card, param={'card': card}, size=size,
                                              bg_color=(0, 0, 0, 0))
                        self.buttons.append(b)
                self.update_board()

                """ VILLAINS BUTTONS """
                self.update_villains()
                left, top = 300, 300
                size = 70, 40
                center = left + 675 + len(self.engine.active_villains) * -200
                font_size = 22
                for i, villain in enumerate(self.engine.active_villains):

                    self.buttons.append(common.Button((center + i * 200, top + 130), "-1", font_size=font_size, size=size,
                                                      function=self.assign_token, param={'villain': villain, 'nb': -1}))
                    self.buttons.append(common.Button((200+center + i * 200, top + 130), "+1", font_size=font_size, size=size,
                                                      function=self.assign_token, param={'villain': villain, 'nb': 1}))

                """ END TURN BUTTON """

                endbutton = common.Button((820, 500), "Fin du tour", self.endturn)
                self.buttons.append(endbutton)

                self.update_location()

    def heroheal(self, nb, character: Character):
        self.engine.heroheal(nb, character)
        self.engine.action_request = None
        self.action_request = None

    def select_card(self, card: Hogwarts, action=None):
        """ Select a card from the hand """
        if "choice" in card.mechanics.keys() and action is None:
            self.action_request = "CHOICE"
            self.choice = card.mechanics["choice"]
            self.temp = card
        elif action is not None:
            self.engine.play_card(card, action)
            self.action_request = None
            self.choice = []
            self.temp = None
        else:
            self.engine.play_card(card)



    def buy_card(self, card, topdeck=None):
        card.active = False
        card.update()
        if topdeck is None:
            self.temp = card
            if "TOPDECK_SPELL" in self.engine.active_character().effects and card.genre == "sort":
                self.action_request = "TOPDECK"
                self.choice = ["TOPDECK", "DISCARD"]
            elif "TOPDECK_OBJECT" in self.engine.active_character().effects and card.genre == "objet":
                self.action_request = "TOPDECK"
                self.choice = ["TOPDECK", "DISCARD"]
            elif "TOPDECK_ALLY" in self.engine.active_character().effects and card.genre == "allié":
                self.action_request = "TOPDECK"
                self.choice = ["TOPDECK", "DISCARD"]
            else:
                self.engine.buy_card(card)
                self.temp = None
        else:
            ch = {"TOPDECK": False, "DISCARD": True}
            self.engine.buy_card(card, ch[topdeck])
            self.action_request = None
            self.choice = []
        self.update_board()

    def choose_first_player(self, character):
        if character is False:
            self.engine.next_player()
            self._update_game()
        else:
            self.first_player = character
            self.banner(f"C'est {character.firstname} qui commence !")
            for p in self.engine.characters:
                if p.name == character:
                    self.engine.set_starter_player(p)
                    self.update_character()
            self.buttons = []
            self.start_turn()

    def start_turn(self):
        self.engine.update_villainseffects()
        self.engine.darkartsevent()
        sugar = self.engine.da_discard[0]
        self.banner(sugar.name, toptext="Evènement Forces du Mal", bottomtext=sugar.description)
        sugar.update()
        self.engine.villainabillities()


    def banner(self, text, toptext="", bottomtext=""):
        """ Show a banner on top of the screen for x seconds """
        if not self.banner_flag:
            self.banner_flag = True
            pygame.draw.rect(self.banner_surf, (0, 0, 0, 192), (0, 200, 1920, 400))
            t = AQUIFER[24].render(toptext, True, 'yellow')
            self.banner_surf.blit(t, ((RESOLUTION[0]-t.get_width())/2, ((RESOLUTION[1]-t.get_height())/2-250)))

            r = ENCHANTED[60].render(text, True, 'white')
            self.banner_surf.blit(r, ((RESOLUTION[0]-r.get_width())/2, ((RESOLUTION[1]-r.get_height())/2-200)))

            b = AQUIFER[20].render(bottomtext, True, 'grey')
            self.banner_surf.blit(b,
                                  ((RESOLUTION[0] - b.get_width()) / 2, ((RESOLUTION[1] - b.get_height()) / 2 - 100)))
        else:
            item = {'text': text, 'toptext': toptext, 'bottomtext': bottomtext}
            if item not in self.banner_queue:
                self.banner_queue.append(item)


    def update_location(self):
        """ Draw the location card on self.image """
        location = self.engine.locations[0]
        location.update()
        #self.image.blit(location.image, (10, 10))

    def update_villains(self):
        for villain in self.engine.active_villains:
            villain.update()

    def assign_token(self, villain, nb):
        active = self.engine.characters[0]
        if active.attack >= nb and villain.attack_tokens + nb >= 0:
            villain.assign_token(nb)
            self.update_villains()
            active.attack -= nb
        self.engine.check_villain_death()

    def update_darkarts(self):
        darkarts = self.engine.da_discard[0]
        darkarts.update()

    def update_board(self):
        for card in self.engine.board:
            if card is not None:
                card.update()


    def update_character(self):
        for i, char in enumerate(self.engine.characters):
            if i == 0:
                char.active = True
            else:
                char.active = False
            char.update()
            char.update_image()
            if char.stunned and not char.has_discarded:
                self.banner(f"{char.firstname} est étourdi(e) !")


    def endturn(self):
        """ ENGINE ENDTURN """
        self.engine.endturn()
        if self.engine.game_over is None:
            self.start_turn()
        else:
            if self.engine.game_over:
                self.banner("GAME OVER")
            else:
                self.banner("VICTOIRE !")



    def get_event(self, event):
        if event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                for b in self.buttons:
                    if b.rect.collidepoint(event.pos) and b.function is not None:
                        if b.param is None:
                            b.function()
                        else:
                            b.function(**b.param)
                        self._update_game()
                        break

    def select_discarded(self, card):
        if card in self.discarded:
            self.discarded.remove(card)
        else:
            self.discarded.append(card)

    def confirm_discard(self, cards, villain):
        for card in cards:
            self.engine.discard_card(self.discard_char, card, villain)
        self.discard_flag = False
        self.discard_nb = 0
        self.discard_char = None
        self.engine.action_request = None
        self.discarded = []




    """ DRAW FUNCTIONS """
    def _draw_location(self, screen: pygame.Surface):
        location = self.engine.locations[0]
        screen.blit(location.image, (0,0))

    def _draw_darkartsevent(self, screen: pygame.Surface):
        if len(self.engine.da_discard) > 0:
            darkartsevent = self.engine.da_discard[0]
            screen.blit(darkartsevent.image, (10, 155))
        """ EFFECTS """
        txt_dict = {"CONTROL_DAMAGEACTIVE_2": "Chaque fois qu'une marque est ajoutée sur le Lieu, le Héros actif perd 2 coeurs",
                    "FORCED_DISCARD_DAMAGE_1": "Chaque fois qu'un Ennemi ou un évènement Forces du Mal oblige un Héros à défausser une carte, ce Héros perd également 1 coeur.",
                    "CANT_PICK": "Vous ne pouvez plus piocher de cartes"}
        if len(self.engine.effects) > 0:
            effects = AQUIFER[20].render("Effets en cours :", True, 'white')
            screen.blit(effects, (10, 400))
            for i, eff in enumerate(self.engine.effects):
                txt = AQUIFER[20].render(txt_dict[eff], True, 'white')
                screen.blit(txt, (10, 440 + i *40))

    def _draw_board(self, screen):
        for i, card in enumerate(self.engine.board):
            if card is not None:
                position = (1300 + (i % 3 * 200), 10 + (i % 2 * 265))
                screen.blit(card.image, (position[0], position[1]))

    def _draw_villains(self, screen):
        left, top = 300, 155
        width, height = 950, 300

        #pygame.draw.rect(screen, 'green', (left, top, width, height))

        ennemi_restants = FONT[24].render(f"Ennemis restants : {len(self.engine.villains)}", True, 'white')
        screen.blit(ennemi_restants, (left + width/2, top))
        center = left + 675 + len(self.engine.active_villains) * -200
        for i, villain in enumerate(self.engine.active_villains):
            screen.blit(villain.image, (center + i * 200, top + 30))

    def _draw_characters(self, screen):
        """ DRAW CHARACTER BOARD """
        """ BACKGROUND """
        BG_COLOR = 46, 43, 25
        pygame.draw.rect(screen, BG_COLOR, (0, 550, RESOLUTION[0], RESOLUTION[1] - 600))

        """ DRAW OTHERS PLAYERS """
        if len(self.engine.characters) > 1:
            for i, char in enumerate(self.engine.characters[1:]):
                screen.blit(char.image, (1430 + i * 155, 550))

        """ UPDATE """
        active = self.engine.characters[0]

        """ BLIT ACTIVE """
        screen.blit(active.image, ((RESOLUTION[0] - active.rect.width) / 2, 550))

        """ EFFECTS """
        for i, elt in enumerate(active.effects):
            txt = FONT[20].render(elt, True, 'white')
            screen.blit(txt, (380, 550 + i * 20))

        """ TRIGGERS """
        for i, elt in enumerate(active.triggers):
            txt = FONT[20].render(str(elt), True, 'white')
            screen.blit(txt, (150, 550 + i * 20))

        """ BLIT CARDS """

        for i, card in enumerate(active.hand):
            posx = (RESOLUTION[0] - (len(active.hand) * 200)) / 2
            position = (posx + i * 200, 755)
            screen.blit(card.image, position)


        """ BLIT DECK """
        if len(active.deck) > 0:
            recto = Recto()
            screen.blit(pygame.transform.rotate(recto.image, -90), (495, 550))

        txt_deck = FONT[18].render(f"Deck : {len(active.deck)}", True, 'white')
        screen.blit(txt_deck, (700, 740))

        """ DRAW PLAYED CARDS """
        if len(active.played) > 0:
            screen.blit(active.played[-1].image, (10, 600))

        if len(active.discard_pile) > 0:
            discard = pygame.transform.rotate(active.discard_pile[-1].image, -90)
            screen.blit(discard, (1165, 550))
        txt_discard = FONT[18].render(f"Défausse : {len(active.discard_pile)}", True, 'white')
        screen.blit(txt_discard, (1170, 740))




    def _draw_discardpanel(self, screen):
        size = 800, 600
        position = 560, 240
        pygame.draw.rect(screen, (0,0,0,192), (position[0], position[1], size[0], size[1]))
        for i, card in enumerate(self.discard_char.hand):
            delta = 0
            if card in self.discarded:
                delta = 30
            pos = (5 + position[0] + i * (card.rect.width + 5), position[0] + delta - 200)
            cardsize = card.rect.width, card.rect.height
            screen.blit(card.image, pos)
            self.buttons.append(common.Button(pos, "", self.select_discarded, cardsize, {'card': card}, (0, 0, 0, 0)))

    def draw(self, screen):
        #screen.blit(self.image, (0,0))
        screen.fill('black')
        self._draw_location(screen)
        self._draw_darkartsevent(screen)
        self._draw_board(screen)
        self._draw_villains(screen)
        self._draw_characters(screen)
        if self.discard_flag:
            self._draw_discardpanel(screen)
        for i, b in enumerate(self.buttons):
            screen.blit(b.image, b.rect)


        screen.blit(self.banner_surf, (0,0))






