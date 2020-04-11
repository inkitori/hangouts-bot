"""
classes for rpg
"""
import utils
from player_class import Stats, Player


class Enemy():
    """represents an enemy"""

    def __init__(self):
        self.stats = Stats(True, True, "enemy")

    def name(self):
        return utils.get_key(RPG.enemies, self)

    def to_dict(self):
        return {"stats": self.stats.to_dict()}


class Room():
    """represents a room in the world"""

    def __init__(self, enemies_list=[], min_level=1, xp_range=(0, 0)):
        self.enemies_list = enemies_list
        self.min_level = min_level
        self.xp_range = xp_range

    def name(self):
        return utils.get_key(RPG.rooms, self)


class Item():
    """represents an item"""

    rarities = ("common", "uncommon", "rare", "legendary")

    def __init__(
        self, type_, rarity=0, modifier="boring",
        health=0, attack=0, defense=0, mana=0
    ):
        self.type_ = type_
        self.rarity = rarity
        self.modifier = modifier
        self.stats = Stats(False, False, "item", health=health, attack=attack, defense=defense, mana=mana)

    def description(self):
        """returns text description of item"""
        return f"{Item.rarities[self.rarity]} {self.modifier} {self.name()}\n"

    def name(self):
        return utils.get_key(RPG.all_items, self)


class RPG():
    """the RPG"""

    all_items = {
        "starter armor": Item("armor"),
        "starter weapon": Item("weapon"),
        "clarity tome": Item("tome")
    }
    players = {}
    rooms = {
        "village": Room()
    }
    enemies = {}

    def register(self, user):
        """registers a user in the game"""
        userID = user.id_[0]
        if userID in self.players:
            return "You are already registered!"
        self.players[userID] = Player("placeholder name")

        return "Successfully registered!"

    def play_game(self, user, commands):
        pass
