from Character import *
from random import choice

class Action:
    def __init__(self, kind: str, rawdata: str):
        self.kind = kind  # instant, choice, choiceall, effect, trigger or in_hand
        self.rawdata = rawdata  # raw data

        self.action = None
        self.effect = None
        self.choice = []
        self.nb = 0

        self.selected = None

        self.ready = False

        self._parse()

    def _parse(self):
        if self.kind == "instant":
            if len(self.rawdata.split('_')) == 2:
                self.action, nb = self.rawdata.split('_')
                self.nb = int(nb)
                self.ready = True
        elif self.kind == "effect":
            if len(self.rawdata.split('_')) == 1:
                self.effect = self.rawdata
                self.ready = True
        elif self.kind == "choiceall":
            self.choice = [Action("choice", elt) for elt in self.rawdata]
        else:
            raise ValueError(self.kind)



class GameEngine:
    def __init__(self, characters, year):
        self.game_over = None

        self.characters = characters
        self.year = year

        self.first_player = None
        self.turn = 0

        self.locations = import_locations(year)  # Le lieu
        self.villains = import_villains(year)  # Les ennemis
        self.darkarts = import_darkarts(year)  # Les cartes forces du mal
        self.da_discard = Deck()  # La défausse forces du mal
        self.hogwarts = import_hogwarts(year)  # Les cartes poudlard
        self.hogwarts_discard = Deck()  # La défausse cartes poudlard

        self.active_villains = Deck()  # Les ennemis en jeu
        self.board = OrderedDeck()  # Les 6 cartes poudlard

        self.trigger = []
        self.effects = []
        self.choice = []

        self.log = []
        self.action_request = None
        self.action_value = 0

        self.action_dict = {"ATTACKSELF": self.attackself,
                            "HEALSELF": self.healself,
                            "HEROHEAL": self.heroheal,
                            "HEALALL": self.healall,
                            "INFLUENCESELF": self.influenceself,
                            "INFLUENCEALL": self.influenceall,
                            "INFLUENCEHERO": self.influencehero,
                            "PICKSELF": self.pickself,
                            "PICKALL": self.pickall,
                            "DAMAGEACTIVE": self.damageactive,
                            "DAMAGEALL": self.damageall,
                            "CONTROL": self.control,
                            "DISCARDACTIVE": self.discardactive,
                            "COPYALLY": self.copyally}

    """ ACTION """
    def copyally(self, card: Hogwarts):
        pass

    def discardactive(self, nb):
        self.action_request = f"DISCARDACTIVE_{nb}"
        self.choice = self.get_active_player_hand()

    def control(self, nb):
        if not self.get_currentlocation().is_dead():
            self.get_currentlocation().add_token(nb)
            if "CONTROL_DAMAGEACTIVE_2" in self.effects and nb > 0:
                self.characters[0].get_damage(2)

    def damageactive(self, nb):
        if "MAXDAMAGE_1" in self.active_character().effects:
            nb = 1
        self.active_character().get_damage(nb)

    def damageall(self, nb):
        for char in self.characters:
            if "MAXDAMAGE_1" in char.effects:
                char.get_damage(1)
            else:
                char.get_damage(nb)

    def attackself(self, nb):
        self.active_character().gain_attack(nb)

    def healself(self, nb):
        self.active_character().heal(nb)

    def heroheal(self, nb, character: Character):
        character.heal(nb)

    def healall(self, nb):
        for char in self.characters:
            char.heal(nb)

    def influenceself(self, nb):
        self.active_character().gain_influence(nb)

    def influenceall(self, nb):
        for char in self.characters:
            char.gain_influence(nb)

    def influencehero(self, nb, hero: Character):
        hero.gain_influence(nb)

    def pickself(self, nb):
        if "CANT_PICK" not in self.effects:
            self.active_character().pick(nb)

    def pickall(self, nb):
        if "CANT_PICK" not in self.effects:
            for char in self.characters:
                char.pick(nb)

    """ GETTERS """
    def get_currentlocation(self) -> Location:
        return self.locations[0]

    def get_active_player_hand(self):
        return self.characters[0].hand

    def active_character(self) -> Character:
        return self.characters[0]

    """ START THE GAME """
    def set_starter_player(self, player: Character):
        """ Someone decided the starting player """
        self.log.insert(0, f"C'est {player} qui commence")
        while self.characters[0] != player:
            self.next_player()

    def pick_villains(self):
        """ Place the villains on the board """
        active_villains_by_year = {1: 1, 2: 1}
        while len(self.active_villains) < active_villains_by_year[self.year]:
            villain = self.villains.pick()
            self.active_villains.append(villain)
            self.log.insert(0, f"{villain} arrive sur le plateau")

    def draw_board(self):
        """ There must be 6 Hogwarts cards on the board at the beginning of the turn """
        while self.board.get_vacant() > 0:
            if len(self.hogwarts) == 0:
                self.hogwarts_discard.shuffle()
                self.hogwarts = self.hogwarts_discard
                self.hogwarts_discard = Deck()
            card = self.hogwarts.pick()
            self.board.add(card)
            self.log.insert(0, f"{card} est posé dans les cartes Poudlard")

    def next_player(self):
        """ Rotation of the active player """
        temp = self.characters.pop(0)
        self.characters.append(temp)

    def execute_action(self, action: Action):
        if action.ready:
            if action.kind == "instant":
                self.action_dict[action.action](action.nb)
            if action.kind == "effect":
                self.effects.append(action.effect)
        else:
            if action.kind == "choiceall":
                self.action_request = "choiceall"
                self.choice = {c: action.choice for c in self.characters}


    """ START THE TURN """


    def darkartsevent(self):
        """ First thing to do every turn """
        da_event = self.darkarts.pick()
        self.log.insert(0, f"L'évènement forces du mal est : {da_event}")
        if len(self.darkarts) == 0:
            self.da_discard.shuffle()
            self.darkarts, self.da_discard = self.da_discard, Deck()
        self.da_discard.insert(0, da_event)
        for key, event in da_event.mechanics.items():
            for action in event:
                a = Action(key, action)
                self.execute_action(a)

        self.detect_stunned()

    def detect_stunned(self):
        for hero in self.characters:
            if hero.health <= 0 and not hero.stunned:
                self.set_stunned(hero)


    def update_villainseffects(self):
        for villain in self.active_villains:
            for key, event in villain.mechanics.items():
                if key == 'effect':
                    for effect in event:
                        self.effects.append(effect)


    def villainabillities(self):
        """ Second thing to do every turn """
        for villain in self.active_villains:
            for key, event in villain.mechanics.items():
                if key == "instant":
                    for effect in event:
                        effect_type = effect.split('_')[0]
                        if effect_type == "DAMAGEACTIVE":
                            self.characters[0].get_damage(int(effect.split('_')[1]))
        self.detect_stunned()


    def clear_effects(self):
        self.effects = []

    def endturn(self):
        for char in self.characters:
            if char.stunned:
                char.stunned = False
                char.has_discarded = False
                char.health = 10

        self.active_character().clear_effects()

        location = self.locations[0]
        if location.control_nb == location.control_nb_max:
            self.locations.remove(location)
        if len(self.locations) == 0:
            self.game_over = True
        else:
            for villain in self.active_villains:
                villain.endturn()
            else:
                self.pick_villains()
                self.draw_board()
                self.active_character().endturn()
                self.next_player()
        self.effects = []

    """ PLAYER FUNCTIONS """
    def play_card(self, card: Hogwarts, action=None):
        self.active_character().play(card)

        # RON EXCEPTION
        if "ATTACKSELF_1_PER_ALLY" in self.active_character().effects and card.genre == "allié":
            self.active_character().gain_attack(1)

        # GENERAL
        for key, event in card.mechanics.items():
            # INSTANT
            if key == "instant":
                for effect in event:
                    n_action, nb = effect.split('_')
                    if action is None:
                        self.action_dict[n_action](int(nb))
                    else:
                        self.action_dict[n_action](int(nb), action)
            # CHOICE ?
            if key == "choice":
                if type(action) == Character:
                    func, nb = card.mechanics['choice'][0].split('_')
                    self.action_dict[func](int(nb), action)
                else:
                    n_action, nb = action.split('_')
                    self.action_dict[n_action](int(nb))
            if key == "effect":
                for effect in event:
                    self.active_character().effects.append(effect)
                    if effect == "ATTACKSELF_1_PER_ALLY":
                        for card in self.active_character().played:
                            if card.genre == "allié":
                                self.active_character().gain_attack(1)
            if key == "trigger":
                self.active_character().triggers.append(event)

    def check_villain_death(self):
        """ CHECK IF VILLAIN IS DEAD AT EVERY ACTION """
        for villain in self.active_villains:
            if villain.is_dead():
                self.active_villains.remove(villain)
                for action in villain.mechanics['reward']:
                    act, nb = action.split('_')
                    self.action_dict[act](int(nb))
                for trigger in self.active_character().triggers:
                    if trigger[0] == "VILLAINDEAD":
                        action, nb = trigger[1].split("_")
                        if action == "HEROHEAL":
                            self.action_request = action+'_'+nb
                            self.action_value = int(nb)
                        else:
                            self.action_dict[action](int(nb))

        if len(self.villains) == 0 and len(self.active_villains) == 0:
            self.game_over = False

    def set_stunned(self, character: Character):
        if not character.has_discarded:
            character.influence = 0
            character.attack = 0
            character.health = 0
            self.action_request = f"DISCARDCHAR_{len(character.hand)//2}"
            character.stunned = True
            character.has_discarded = False
            self.control(1)

    def stun_discard(self, character, cards):
        for card in cards:
            self.discard_card(character, card)
        character.has_discarded = True

    def discard_card(self, character, card, villain=False):
        character.discard(card)
        if villain and "FORCED_DISCARD_DAMAGE_1" in self.effects:
            character.get_damage(1)
        if "trigger" in card.mechanics.keys():
            for trigger, effect in card.mechanics["trigger"]:
                if trigger == "DISCARDEDSELF":
                    effect, nb = effect.split("_")
                    self.action_dict[effect](nb, character)

    def buy_card(self, card: Hogwarts, discard=True):
        player = self.active_character()
        if card.cost <= player.influence:
            self.board.remove(card)
            player.buy(card, discard)
        else:
            raise ValueError(f"{player.firstname} n'a pas assez de mornilles ({player.influence}) pour acheter {card} ({card.cost})")

