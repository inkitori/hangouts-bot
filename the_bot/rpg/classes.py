"""
classes for rpg
"""
import utils
import random
import enum
import math


class Stats:
    """class for stats"""

    def __init__(
        self, *, generate_stats=False,
        max_health=None, health=None, mana=None, attack=None, defense=None,
        max_mana=None, level=None, exp=None, balance=None, lifetime_balance=None
    ):
        # TODO: get rid of init arguments and take **kwargs
        if generate_stats:
            attack, defense, health = self.generate_from_level(level)
        if health is not None:
            self._health = int(health)
            self._max_health = max(utils.default(max_health, 1), self.health)
        if mana is not None:
            self._mana = int(mana)
            self._max_mana = max(utils.default(max_mana, 0), self.mana)
        if balance is not None:
            self._balance = int(balance)
            self._lifetime_balance = max(
                utils.default(lifetime_balance, 0), self.balance
            )
        level = utils.default(0, level, exp)
        self.level = level if not level else int(level)
        exp = utils.default(0, exp, level)
        self._exp = exp if not exp else int(exp)
        self.attack = attack if not attack else int(attack)
        self.defense = defense if not defense else int(defense)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, new_balance):
        if new_balance > self._balance:
            self.lifetime_balance += new_balance - self._balance
        self._balance = new_balance

    @balance.deleter
    def balance(self):
        del self._balance

    @property
    def lifetime_balance(self):
        return self._lifetime_balance

    @lifetime_balance.setter
    def lifetime_balance(self, new_balance):
        self._lifetime_balance = utils.default(
            new_balance, self._lifetime_balance,
            new_balance > self._lifetime_balance
        )

    @lifetime_balance.deleter
    def lifetime_balance(self):
        del self._lifetime_balance

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, new_health):
        """changes player health"""
        if new_health == "full":
            self._health = self.max_health
            return

        self._health = round(new_health, 1)
        self._health = utils.clamp(self._health, 0, self.max_health)

    @health.deleter
    def health(self):
        del self._health

    @property
    def max_health(self):
        return self._max_health

    @max_health.setter
    def max_health(self, new_max_health):
        """changes player health"""
        self.health += new_max_health - self._max_health
        self._max_health = int(utils.default(
            new_max_health, 0, new_max_health > 0))

    @max_health.deleter
    def max_health(self):
        del self._max_health

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, new_mana):
        """changes player mana"""
        if new_mana == "full":
            self._mana = self.max_mana
            return

        self._mana = round(new_mana, 1)
        self._mana = utils.clamp(self._mana, 0, self.max_mana)

    @mana.deleter
    def mana(self):
        del self._mana

    @property
    def max_mana(self):
        return self._max_mana

    @max_mana.setter
    def max_mana(self, new_max_mana):
        """changes player health"""
        self.mana += new_max_mana - self._max_mana
        self._max_mana = int(utils.default(new_max_mana, 0, new_max_mana > 0))

    @max_mana.deleter
    def max_mana(self):
        del self._max_mana

    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, new_exp):
        """increases exp"""
        notify = False
        self._exp = new_exp
        exp_required = self.next_level_exp()

        while self._exp > exp_required:
            self.level += 1
            self._exp -= exp_required
            notify = True
            exp_required = self.next_level_exp()
        if notify:
            return f"You are now level {self.level}!"

        return ""

    @exp.deleter
    def exp(self):
        del self._exp

    def generate_from_level(self, level):
        """generates stats from level"""
        attack = 5 * level ** 1.8
        defense = 5 * level ** 1.5
        health = 100 * level ** 2
        return [round(stat) for stat in (attack, defense, health)]

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
                if stat_name not in ("level", "exp") and stat_value is not None
            ], description_mode="short", separator="\n\t"
        )
        if self.level is not None:
            stats_text += "\t" + self.print_level_exp()
        return stats_text

    def next_level_exp(self):
        """returns next level exp"""
        return round(4 * (((self.level + 1) ** 4) / 5))

    def print_level_exp(self):
        """returns string representation of level and exp"""
        return f"LVL: {self.level} | {self.exp} / {self.next_level_exp()}"


class Enemy:
    """represents an enemy"""

    def __init__(self, name, level=1, attack=0, defense=0, health=1):
        self.name = name
        self.stats = Stats(
            generate_stats=True, level=level,
            attack=attack, defense=defense, health=health
        )

    def attack(self, player):
        """"""
        damage_dealt = round(
            self.stats.attack /
            (player.modified_stats().defense + player.stats.defense), 1
        )

        multiplier = random.choice((1, -1))
        damage_dealt += round(multiplier * math.sqrt(damage_dealt / 2), 1)

        player.stats.health -= damage_dealt

        text = utils.join_items(
            f"{self.name} dealt {damage_dealt} to you!",
            f"You have {player.stats.health} hp left",
            f"{self.name} has {self.stats.health} left!",
        )
        return text


class Room:
    """represents a room in the world"""

    def __init__(
        self, level=1, enemies_list=[], boss=None, min_level=1,
        can_rest=False, drops=None
    ):
        self.level = level
        self.enemies_list = enemies_list
        self.boss = boss
        self.drops = drops
        self.min_level = min_level
        self.can_rest = can_rest

    def name(self):
        return utils.get_key(rooms, self)

    def generate_enemy(self):
        enemy = random.choice(self.enemies_list)
        return enemy.name, enemy

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
class ItemModifer(enum.Enum):
    CRAPPY = Stats(health=-5, mana=-5, attack=-5, defense=-5)
    BORING = Stats(health=0, mana=0, attack=0, defense=0)
    STRONG = Stats(health=5, mana=5, attack=5, defense=5)


class Item:
    """represents an item"""

    def __init__(
        self, type_, *, name, rarity=1, modifier="boring", price=1,
        health=0, attack=0, defense=0, mana=0, level=1,
        description="what, you thought we would write flavor text for everything? pft"
    ):
        self.name = name
        self.type_ = ItemType(type_.lower())
        self.rarity = Rarity(int(rarity))
        self.modifier = modifier
        self.stats = Stats(
            generate_stats=False, health=health, attack=attack,
            defense=defense, mana=mana, level=level,
        )
        self.description = description

    def get_description(self):
        """returns text description of item"""
        return utils.description(
            utils.join_items(
                self.rarity.name.lower(), self.full_name(),
                separator=" ", newlines=0
            ),
            self.description, newlines=0
        )

    def full_name(self):
        return utils.join_items(self.modifier, self.name, separator=' ', newlines=0)


all_items = {
    "starter armor": Item(name="starter armor", type_="armor", defense=5),
    "starter weapon": Item(name="starter weapon", type_="weapon", attack=5),
    "clarity tome": Item(name="clarity tome", type_="tome", health=20, mana=5),
}

rooms = {
    "village": Room(can_rest=True),
    "potatoland": Room(enemies_list=[Enemy("potato"), Enemy("super potato", level=3)]),
}
