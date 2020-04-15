"""
classes for rpg
"""
import utils
import random
import copy
import enum


class Stats():
    """class for stats"""
    def __init__(
        self, *, alive=False, generate_stats=False, type_=None,
        max_health=0, health=0, mana=0, attack=0, defense=0,
        max_mana=0, level=1, xp=0, balance=0, lifetime_balance=0
    ):
        if alive:
            self.max_health = max_health
            self.health = health
        if type_ == "player":
            self.mana = mana
            self.max_mana = max_mana
            self.lifetime_balance = lifetime_balance
            self.balance = balance
            self.xp = xp
        elif type_ == "item":
            self.mana = mana
            self.health = health
        if generate_stats:
            attack, defense, health = self.generate_from_level(level)
        self.attack = attack
        self.defense = defense
        self.level = level

    def to_dict(self):
        return self.__dict__

    def generate_from_level(self, level):
        """generates stats from level"""
        attack = round(5 * level ** 1.8)
        defense = round(5 * level ** 1.5)
        health = round(100 * level ** 2)
        return attack, defense, health

    def print_stats(self, modifiers=None):
        """returns text representation of stats"""
        stats_text = utils.join_items(
            *[
                (stat_name, stat_value)
                for stat_name, stat_value in self.__dict__.items()
                if stat_name not in ("level", "xp")
            ], is_description=True
        )
        try:
            stats_text += self.print_level_xp()
        except AttributeError:
            pass
        return stats_text

    def next_level_xp(self):
        """returns next level xp"""
        return round(4 * (((self.level + 1) ** 4) / 5))

    def print_level_xp(self):
        """returns string representation of level and xp"""
        return f"LVL: {self.level} | {self.xp} / {self.next_level_xp()}"

    def increase_balance(self, money):
        """increases balance"""
        self.balance += money
        self.lifetime_balance += money

    def give_xp(self, xp_earned):
        """increases xp"""
        notify = False
        self.xp += xp_earned

        xp_required = self.next_level_xp()

        while self.xp > xp_required:
            self.level += 1
            self.xp -= xp_required
            notify = True
            xp_required = self.next_level_xp()
        if notify:
            return f"You are now level {self.level}!"

        return ""

    def change_health(self, amount):
        """changes player health"""
        if amount == "full":
            self.health = self.max_health
            return
        self.health += amount
        self.health = utils.clamp(self.health, 0, self.max_health)


class Enemy():
    """represents an enemy"""

    def __init__(self, stats={}):
        self.stats = Stats(alive=True, generate_stats=True, type_="enemy", **stats)

    def name(self):
        return utils.get_key(enemies, self)

    def to_dict(self):
        return {"stats": self.stats.to_dict()}


class Room():
    """represents a room in the world"""

    def __init__(self, enemies_list=[], min_level=1, xp_range=(0, 0), can_rest=False):
        self.enemies_list = enemies_list
        self.min_level = min_level
        self.xp_range = xp_range
        self.can_rest = can_rest

    def name(self):
        return utils.get_key(rooms, self)

    def generate_enemy(self):
        enemy_name = random.choice(self.enemies_list)
        enemy = copy.deepcopy(enemies[enemy_name])
        return enemy_name, enemy


@enum.unique
class Rarity(enum.IntEnum):
    COMMON = enum.auto()
    UNCOMMON = enum.auto()
    RARE = enum.auto()
    LEGENDARY = enum.auto()


class Item():
    """represents an item"""

    types = ("weapon", "armor", "tome")

    def __init__(
        self, type_, rarity=0, modifier="boring",
        stats={"health": 0, "attack": 0, "defense": 0, "mana": 0}
    ):
        if type_ not in self.types:
            print(f"invalid item type {type_}")
        self.type_ = type_
        self.rarity = Rarity(rarity)
        self.modifier = modifier
        self.stats = Stats(alive=False, generate_stats=False, type_="item", **stats)

    def short_description(self):
        """returns text description of item"""
        return f"{Item.rarities[self.rarity.name.lower()]} {self.modifier} {self.name()}\n"

    def name(self):
        return utils.get_key(all_items, self)

    def to_dict(self):
        return {
            "type_": self.type_,
            "rarity": self.rarity.value,
            "modifier": self.modifier,
            "stats": self.stats.to_dict()
        }


all_items = {
    "starter armor": Item(type_="armor"),
    "starter weapon": Item(type_="weapon", stats={}),
    "clarity tome": Item(type_="tome", stats={"health": 20})
}

rooms = {
    "village": Room(can_rest=True),
    "potatoland": Room(enemies_list=["potato", ])
}
enemies = {
    "potato": Enemy(stats={"health": 20, "max_health": 20, "attack": 1})
}
