"""
classes for rpg
"""
import utils


class Stats():
    """class for stats"""
    def __init__(
        self, alive=False, random_stats=True, type_=None,
        *, max_health=100, health=5, mana=5, attack=5, defense=5, max_mana=100, level=1, xp=0, balance=0
    ):
        if alive:
            self.health = self.max_health = max_health
        if type_ == "player":
            self.mana = self.max_mana = max_mana
            self.lifetime_balance = self.balance = balance
            self.xp = xp
        elif type_ == "item":
            self.mana = mana
            self.health = health
        if random_stats():
            attack, defense, health = self.generate_from_level(level)
        self.attack = attack
        self.defense = defense
        self.level = level

    def generate_from_level(self, level):
        """generates stats from level"""
        # change this joseph
        attack = round(5 * level ** 1.8)
        defense = round(5 * level ** 1.5)
        health = round(100 * level ** 2)
        return attack, defense, health

    def print_stats(self):
        """returns text representation of stats"""
        pass

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


class Player():
    """represents a player in the rpg"""

    def __init__(self, name):
        self.name = name
        self.stats = Stats(True, False, "player")
        self.room = "village"
        self.fighting = ""
        self.inventory = [None for i in range(8)]
        self.add_to_inventory("starter armor", "starter weapon", "clarity")
        self.equipped = {"armor": 0, "weapon": 1, "tome": "clarity"}

    def add_to_inventory(self, items, slot=None):
        """
        puts an item into the first empty slot
        if a slot is specifed, uses that slot instead
        """
        if len(items) < 1:
            return("you must pick an item")
        elif len(items) > 1 and slot:
            return("you can only put in one item at a time if using a slot")
        output_text = ""

        for item_name in items:
            added_text = f"put {item_name} in slot"
            if slot is not None:
                replaced_item_name = utils.get_key(Game.all_items, self.inventory[slot])
                try:
                    self.inventory[slot] = item_name
                except IndexError:
                    return f"slot {slot} does not exist"
                return added_text + f" {slot} replacing {replaced_item_name}"
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = item_name
                    output_text += utils.newline(added_text) + f" {i}"
                output_text += "there are no empty slots, specify a slot"
        return output_text

    def equip(self, item):
        """equips an item"""
        pass

    def print_inventory(self):
        """returns string representation of inventory"""
        inventory_text = ""
        for item_name in self.inventory:
            inventory_text += Game.all_items[item_name].description()
        return inventory_text

    def print_stats(self):
        """returns string representation of stats"""
        # should print stats + modifers from weapons
        return

    def modified_stats(self):
        """returns Stats() of player modified by player.equipped"""
        # should use eqquiped item stats to calculate stats
        # then return a stats obbjcet with those stats
        return

    def print_equipped(self):
        """returns string representation of equipped items"""
        equipped = ""

        for type_, index in self.equipped.items():
            item = Game.all_items[self.inventory[index]]
            equipped += f"{type_}: {item.description()}"

        return equipped.title()

    def warp(self, user, commands):
        """warps to rooms"""
        rooms = Game.rooms
        room = utils.get_item_safe(commands)
        if not room:
            return "Invalid argument! use warp {room}"

        if self.fighting:
            return "You can't warp while in a fight!"

        elif room not in rooms:
            return "That room doesn't exist!"

        elif rooms[room].min_level > self.stats.level:
            return "Your level is not high enough to warp there!"

        elif room == user.room:
            return "You are already in that room!"

        user.room = room
        return "Successfully warped!"

    def rest(self):
        """rests player"""
        text = ""
        if self.room == "village":
            self.stats.change_health("full")
            text += "You feel well rested...\n"
            text += f"Your health is back up to {self.stats.hp}!"
        else:
            text = "You have to rest in the village!"

        return text


class Enemy():
    """represents an enemy"""

    def __init__(self):
        self.stats = Stats(True, True, "enemy")

class Room():
    """represents a room in the world"""

    def __init__(self, enemies_list=[], min_level=1, xp_range=(0, 0)):
        self.enemies_list = enemies_list
        self.min_level = min_level
        self.xp_range = xp_range


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
        return f"{Item.rarities[self.rarity]} {self.modifier} {utils.get_key(Game.all_items, self)}\n"


class Game():
    """game"""

    all_items = {
        "starter armor": Item("armor"),
        "starter weapon": Item("weapon"),
        "clarity tome": Item("tome")
    }
    users = {}
    rooms = {
        "village": Room()
    }
    enemies = {}

    def register(self, user, commands):
        """registers a user in the game"""
        userID = utils.get_key(self.users, user)
        if userID in self.users:
            return "You are already registered!"
        self.users[userID] = Player("placeholder name")

        return "Successfully registered!"
