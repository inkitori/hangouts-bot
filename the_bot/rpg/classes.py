"""
classes for rpg
"""
import utils
import random
import copy
import enum


class Stats:
    """class for stats"""

    def __init__(
        self, *, generate_stats=False,
        max_health=None, health=None, mana=None, attack=None, defense=None,
        max_mana=None, level=None, xp=None, balance=None, lifetime_balance=None
    ):
        # TODO: get rid of init arguments and take **kwargs
        if generate_stats:
            attack, defense, health = self.generate_from_level(level)
        if health is not None:
            self.health = health
            self.max_health = max(utils.default(max_health, 1), health)
        if mana is not None:
            self.mana = mana
            self.max_mana = max(utils.default(max_mana, 0), mana)
        if balance is not None:
            self.balance = balance
            self.lifetime_balance = max(
                utils.default(lifetime_balance, 0), balance)
        self.xp = xp
        self.attack = attack
        self.defense = defense
        self.level = level

    def generate_from_level(self, level):
        """generates stats from level"""
        attack = round(5 * level ** 1.8)
        defense = round(5 * level ** 1.5)
        health = round(100 * level ** 2)
        return attack, defense, health

    def print_stats(self, modifiers=None):
        """returns text representation of stats"""
        # this mess adds a + modifed value if there is a modified stat
        modifiers = utils.default(modifiers, Stats())
        stats_text = utils.join_items(
            *[
                (
                    stat_name, str(stat_value) +
                    utils.default(
                        f" +{modifiers.__dict__.get(stat_name, 0)}",
                        "", modifiers.__dict__.get(stat_name, 0)
                    )
                )
                for stat_name, stat_value in self.__dict__.items()
                if stat_name not in ("level", "xp") and stat_value is not None
            ], is_description=True, separator="\n\t"
        )
        if self.level is not None:
            stats_text += "\t" + self.print_level_xp()
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


class Enemy:
    """represents an enemy"""

    def __init__(self, level=1):
        self.stats = Stats(generate_stats=True, level=level)

    def name(self):
        return utils.get_key(enemies, self)


class Room:
    """represents a room in the world"""

    def __init__(self, enemies_list=[], min_level=1, xp_range=(1, 1), can_rest=False):
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

    def generate_encounter(self, party):
        # trying to figure out how to get parites to work, just leave this alone
        pass


@enum.unique
class Rarity(enum.IntEnum):
    COMMON = enum.auto()
    UNCOMMON = enum.auto()
    RARE = enum.auto()
    EPIC = enum.auto()
    LEGENDARY = enum.auto()


@enum.unique
class ItemType(enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    TOME = "tome"


@enum.unique
class Modifier(enum.Enum):
    CRAPPY = Stats(health=-5, mana=-5, attack=-5, defense=-5)
    BORING = Stats(health=0, mana=0, attack=0, defense=0)
    STRONG = Stats(health=5, mana=5, attack=5, defense=5)


class Item:
    """represents an item"""

    def __init__(
        self, type_, rarity=1, modifier="boring",
        stats={"health": 0, "attack": 0, "defense": 0, "mana": 0, "level": 1, }
    ):
        self.type_ = ItemType(type_)
        self.rarity = Rarity(rarity)
        self.modifier = modifier
        self.stats = Stats(generate_stats=False, **stats)

    def short_description(self):
        """returns text description of item"""
        return f"{self.rarity.name.lower()} {self.modifier} {self.name()}"

    def name(self):
        return utils.get_key(all_items, self)

    def full_name(self):
        return utils.join_items(self.modifier, self.name(), separator=' ', newlines=0)


all_items = {
    "starter armor": Item(type_="armor", stats={"defense": 5}),
    "starter weapon": Item(type_="weapon", stats={"attack": 5}),
    "clarity tome": Item(type_="tome", stats={"health": 20, "mana": 5})
}

rooms = {
    "village": Room(can_rest=True),
    "potatoland": Room(enemies_list=["potato", "super potato"])
}
enemies = {
    "potato": Enemy(),
    "super potato": Enemy(3),
}
