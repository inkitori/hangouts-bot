import utils
import random
import math
import classes

class Player():
    """represents a player in the rpg"""

    def __init__(self, name):
        self.name = name
        self.stats = Stats(True, False, "player")
        self.room = "village"
        self.fighting = {}
        self.inventory = [None for i in range(8)]
        self.add_to_inventory("starter armor", "starter weapon", "clarity")
        self.equipped = {"armor": 0, "weapon": 1, "tome": 2}

    def id(self):
        return utils.get_key(RPG.players, self)

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
                replaced_item_name = self.inventory[slot]
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

    def unequip(self, item):
        pass

    def get_equipped(self, type_):
        item_name = self.inventory[self.equipped[type_]]
        item = RPG.all_items[item_name]
        return item

    def print_inventory(self):
        """returns string representation of inventory"""
        inventory_text = ""
        for item_name in self.inventory:
            inventory_text += RPG.all_items[item_name].description()
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
            item = RPG.all_items[self.inventory[index]]
            equipped += f"{type_}: {item.description()}"

        return equipped.title()

    def warp(self, commands):
        """warps to rooms"""
        output_text = ""
        rooms = RPG.rooms
        room = next(commands)
        if not room:
            output_text = "Invalid argument! use warp {room}"
        elif self.fighting:
            output_text = "You can't warp while in a fight!"

        elif room not in rooms:
            output_text = "That room doesn't exist!"

        elif rooms[room].min_level > self.stats.level:
            output_text = "Your level is not high enough to warp there!"

        elif room == self.room:
            output_text = "You are already in that room!"
        else:
            self.room = room
            output_text = "Successfully warped!"
        return output_text

    def to_dict(self):
        player_dict = {
            "name": self.name,
            "stats": self.stats.to_dict(),
            "room": self.room,
            "fighting": {enemy_name: enemy.to_dict() for enemy_name, enemy in self.fighting.items()},
            "inventory": self.inventory,
            "equipped": self.equipped
        }
        return player_dict

    def rest(self):
        """rests player"""
        text = ""
        if self.room == "village":
            self.stats.change_health("full")
            text += utils.join_items(
                "You feel well rested...\n",
                f"Your health is back up to {self.stats.hp}!",
            )
        else:
            text = "You have to rest in the village!"

        return text

    def heal(self):
        """heal the player with their tome"""
        tome_stats = self.equipped["tome"].stats
        if self.stats.mana < tome_stats.mana:
            return "You do not have enough mana to heal!"

        else:
            self.stats.mana -= tome_stats.mana
            self.stats.change_health(tome_stats.health)

            return f"You have been healed back up to {self.stats.health}"

    def attack(self, enemy):
        """attacks an enemy"""
        text = ""

        if not self.fighting:
            return "You need to be in a fight!"

        enemy = RPG.enemies[self.fighting]
        user_damage = self.modified_stats().attack
        damage_dealt = (user_damage) * (user_damage / enemy.defense)

        multiplier = random.choice((1, -1))
        damage_dealt += int(multiplier * math.sqrt(damage_dealt / 2))
        enemy.stats.health -= damage_dealt

        text += f"You dealt {damage_dealt} damage to {enemy.name()}!\n"

        if enemy.stats.health <= 0:
            text = self.killed_enemy(enemy)

        else:
            # take damage
            damage_taken = enemy.attack / self.modified_stats().defense

            multiplier = random.choice((1, -1))
            damage_taken += int(multiplier * math.sqrt(damage_taken / 2))

            self.stats.change_health(- damage_taken)

            text += utils.join_list(
                f"{enemy.name} dealt {damage_taken} to you!",
                f"You have {self.stats.hp} hp left",
                f"{enemy.name} has {enemy.stats.health} left!"
            )

            if self.stats.health <= 0:
                text += f"You were killed by {enemy.name}..."

                self.fighting = ""
                self.stats.change_health("full")

        return text

    def killed_enemy(self, enemy):
        """changes stuff based on enemy"""
        text = ""
        text += f"{enemy.name} is now dead!\n"

        xp_range = RPG.rooms[self.room].xp_range
        xp_earned = random.randint(*xp_range)

        gold_earned = int(enemy.max_health / 10) + random.randint(1, 10)

        text += f"You earned {xp_earned} xp and {gold_earned} gold!"
        text += self.stats.give_xp(xp_earned)

        self.stats.increase_balance(gold_earned)
        self.fighting = ""

        return text

    def fight(self):
        """starts a with an enemy"""
        rooms = RPG.rooms["rooms"]
        text = ""

        # DO NOT let an if elif chain happen here
        if self.room == "village":
            text = "Don't fight in the village..."

        elif self.fighting:
            text = f"You are already fighting {self.fighting}!"

        else:
            enemy_name = random.choice(rooms[self.room].enemies_list)
            enemy = RPG.enemies[enemy_name]

            text += f"{enemy_name} has approached to fight!\n"
            text += enemy.stats.print_stats()
            self.fighting = enemy
        return text

    def print_profile(self):
        pass


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