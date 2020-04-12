import utils
import random
import math
import copy
import rpg.classes as classes

class Inventory():
    """player's inventory"""
    def __init__(
        self, items={}, max_items=8,
        equipped={"armor": None, "weapon": None, "tome": None}  # value is item name
    ):
        self.items = {item_name: classes.Item(**item_data) for item_name, item_data in items.items()}
        self.max_items = max_items
        self.equipped = equipped

    def add(self, commands):
        """
        puts an item into the inventory
        """
        item_name = next(commands)
        output_text = ""
        if not item_name:
            output_text = "you must pick an item"
        elif len(self.items) >= self.max_items:
            output_text = "your inventory is full, remove something first"
        else:
            self.items[item_name] = copy.deepcopy(RPG.all_items[item_name])
            output_text = f"added {item_name} to inventory"
        return output_text

    def remove(self, commands):
        item_name = utils.join_items(*list(commands), seperator=" ")
        if not item_name:
            return "you must specify an item"
        elif item_name not in self.items:
            return "you do not have that item"
        elif item_name in self.equipped.values():
            return "you must unequip that item first"
        else:
            del self.items[item_name]
            return f"{item_name} removed from inventory"

    def equip(self, item):
        """equips an item"""
        pass

    def unequip(self, item):
        pass

    def get_equipped(self, type_):
        item_name = self.equipped[type_]
        item = self.inventory[item_name]
        return item_name, item

    def print_inventory(self):
        """returns string representation of inventory"""
        inventory_text = ""
        for item_name, item in self.items.items():
            inventory_text += item.description()
        inventory_text += self.print_equipped()
        return inventory_text

    def print_equipped(self):
        """returns string representation of equipped items"""
        equipped_text = utils.join_items(
            *[
                (type_, self.items[item_name].description)
                for type_, item_name in self.equipped.items()
                if item_name
            ], is_description=True
        )
        """
        for type_, item_name in self.equipped.items():
            item = self.inventory[item_name]
            equipped_text += f"{type_}: {item.description()}"
        """
        return equipped_text.title()

    def _to_dict(self):
        return {
            "items": {item_name: item._to_dict() for item_name, item in self.items.items()},
            "max_items": self.max_items,
            "equipped": self.equipped,
        }

    def modifers(self):
        weapon = self.inventory.get_equipped("weapon")[1]
        armor = self.inventory.get_equipped("armor")[1]
        modified_attack = weapon.stats.attack + armor.stats.attack
        modified_defense = weapon.stats.defense + armor.stats.defense
        return classes.Stats(attack=modified_attack, defense=modified_defense)


class Player():
    """represents a player in the rpg"""

    def __init__(
        self, name,
        stats={},
        room="village", fighting={}, inventory={}
    ):
        self.name = name
        self.stats = classes.Stats(alive=True, type_="player", **stats)
        self.room = room
        self.fighting = {enemy_name: classes.Enemy(**enemy_data) for enemy_name, enemy_data in fighting}
        self.inventory = Inventory(**inventory)

    def id(self):
        return utils.get_key(RPG.players, self)

    def print_stats(self):
        """returns string representation of stats"""
        stats_list = []
        for stat_name, stat in self.stats.__dict__.items():
            stat_text = f"{stat_name}: {stat}"
            if utils.get_value(self.modiifer_stats.__dict__, stat_name):
                stat_text += f" {self.modiifer_stats.__dict__[stat_name]}"
            stats_list.append(stat_text)

        return utils.join_items(stats_list)

    def modified_stats(self):
        """returns Stats() of player modified by player.equipped"""
        modifiers = self.inventory.modifers()
        modified_attack = modifiers.attack + self.stats.attack
        modified_defense = modifiers.defense + self.stats.defense
        return classes.Stats(attack=modified_attack, defense=modified_defense)

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

    def _to_dict(self):
        player_dict = {
            "name": self.name,
            "stats": self.stats._to_dict(),
            "room": self.room,
            "fighting": {enemy_name: enemy._to_dict() for enemy_name, enemy in self.fighting.items()},
            "inventory": self.inventory._to_dict(),
        }
        return player_dict

    def rest(self):
        """rests player"""
        if RPG.rooms[self.room].can_rest:
            self.stats.change_health("full")
            text = utils.join_items(
                "You feel well rested...\n",
                f"Your health is back up to {self.stats.hp}!",
            )
        else:
            text = "You can't rest here!"

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

        enemy = random.choice(self.fighting.values())
        user_damage = self.modified_stats().attack
        damage_dealt = user_damage * (user_damage / enemy.defense)

        multiplier = random.choice((1, -1))
        damage_dealt += int(multiplier * math.sqrt(damage_dealt / 2))
        enemy.stats.change_health(- damage_dealt)

        text += f"You dealt {damage_dealt} damage to {enemy.name()}!\n"

        if enemy.stats.health <= 0:
            text += self.killed_enemy(enemy)

        else:
            # take damage
            damage_taken = enemy.attack / self.modified_stats().defense

            multiplier = random.choice((1, -1))
            damage_taken += int(multiplier * math.sqrt(damage_taken / 2))

            self.stats.change_health(- damage_taken)

            text += utils.join_list(
                f"{enemy.name} dealt {damage_taken} to you!",
                f"You have {self.stats.health} hp left",
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
        self.stats.give_xp(xp_earned)
        self.stats.increase_balance(gold_earned)
        del self.fighting[enemy.name]

        return text

    def fight(self):
        """starts a with an enemy"""
        rooms = RPG.rooms["rooms"]
        text = ""

        # DO NOT let an if elif chain happen here
        if not RPG.rooms[self.room].enemies_list:
            text = "There are no enemies here"

        elif self.fighting:
            text = f"You are already fighting {', '.join(self.fighting.keys())}!"

        else:
            enemy_name = random.choice(rooms[self.room].enemies_list)
            enemy = copy.deepcopy(RPG.enemies[enemy_name])

            text += f"{enemy_name} has approached to fight!\n"
            text += enemy.stats.print_stats()
            self.fighting[enemy_name] = enemy
        return text

    def print_profile(self):
        # print stats
        pass


class RPG():
    """the RPG"""

    all_items = classes.all_items
    players = {}
    rooms = classes.rooms
    enemies = classes.enemies
    help_text = "placeholder help text"

    def __init__(self):
        pass

    def register(self, userID, commands):
        """registers a user in the game"""
        name = next(commands)
        if userID in self.players:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.players[userID] = Player(name=name)
        return "Successfully registered!"

    def play_game(self, userID, commands, command=""):
        """runs functions based on user command"""
        # will be cleaned once everything works for easier testing
        command = command if command else next(commands)
        output_text = ""
        player = utils.get_value(self.players, userID)
        if command == "register":
            output_text = self.register(userID, commands)
        elif command == "help":
            output_text = self.help_text

        # inventory commands
        elif command == "inventory":
            output_text = player.inventory.print_inventory()
        elif command == "add":
            output_text = player.inventory.add()
        elif command == "remove":
            output_text = player.inventory.remove()
        elif command == "equip":
            output_text = player.inventory.equip()
        elif command == "unequip":
            output_text = player.inventory.unequip()

        elif command == "warp":
            output_text = player.warp()
        elif command == "profile":
            output_text = player.print_profile()
        elif command == "equip":
            output_text = player.inventory.equip()
        elif command == "stats":
            output_text = player.print_stats()
        elif command == "rest":
            output_text = player.rest()
        elif command == "fight":
            output_text = player.fight()
        elif command in ("atk", "attack"):
            output_text = player.atk()
        elif command == "heal":
            output_text = player.heal()
        else:
            output_text = "invalid command"

        return output_text
