import utils
import random
import math
import rpg.classes as classes


class Inventory():
    """player's inventory"""
    def __init__(
        self, items={}, max_items=8,
        equipped={"armor": None, "weapon": None, "tome": None}
    ):
        self.items = items
        self.max_items = max_items
        self.equipped = {
            classes.ItemType(type_): item_name
            for type_, item_name in equipped.items()
        }

    def add(self, commands):
        """
        puts an item into the inventory
        """
        item_name = commands.send("remaining")
        output_text = ""
        if not item_name:
            output_text = "you must pick an item"
        elif sum(self.items.values()) >= self.max_items:
            output_text = "your inventory is full, remove something first"
        # this still lets the player add anything if they know the name
        elif item_name not in classes.all_items:
            output_text = "that item does not exist"
        else:
            # increments the value
            self.items[item_name] = utils.get_value(self.items, item_name, default=0) + 1
            output_text = f"added {item_name} to inventory"
        return output_text

    def remove(self, commands):
        item_name = commands.send("remaining")
        if not item_name:
            return "you must specify an item"
        elif item_name not in self.items:
            return "you do not have that item"
        elif item_name in self.equipped.values() and self.items[item_name] == 1:
            return "you must unequip that item first"
        else:
            self.items[item_name] -= 1
            if self.items[item_name] == 0:
                del self.items[item_name]
            return f"{item_name} removed from inventory"

    def equip(self, commands):
        """equips an item"""
        output_text = ""
        item_name = commands.send("remaining")
        if not item_name:
            output_text += "you must specify an item"
        elif item_name not in self.items:
            output_text += "you do not have that item"
        else:
            item_type = classes.all_items[item_name].type_
            current_equipped_item = self.get_equipped(item_type)[0]
            if current_equipped_item == item_name:
                output_text += "you already equipped that"
            else:
                output_text += f"equipping {item_name} as {item_type.name.lower()}"
                self.equipped[item_type] = item_name
                if current_equipped_item:
                    output_text += f" replacing {current_equipped_item}"
        return output_text

    def unequip(self, commands):
        output_text = ""
        name = commands.send("remaining")
        try:
            type_ = classes.ItemType(name)
        except ValueError:
            type_ = None
        if not name:
            output_text = "you must specify an item name or type"
        elif type_:
            if not self.equipped[type_]:
                output_text = "you do not have anything equipped of that type"
            else:
                current_equipped_item = self.equipped[type_]
                self.equipped[type_] = None
                output_text = f"unequipped {current_equipped_item} as {type_.name.lower()}"
        elif name in classes.all_items:
            item_type = classes.all_items[name].type_
            if self.equipped[item_type] != name:
                output_text = "that item is not equipped"
            else:
                self.equipped[item_type] = None
                output_text = f"unequipped {name} as {item_type.name.lower()}"
        else:
            output_text = "invalid type or name"
        return output_text

    def get_equipped(self, type_):
        item_name = self.equipped[type_]
        item = classes.all_items[item_name] if item_name else None
        return item_name, item

    def print_inventory(self, commands):
        """returns string representation of inventory"""
        inventory_text = ""
        # change to use utils.join_items
        for item_name, item_count in self.items.items():
            item = classes.all_items[item_name]
            # TODO: print amount of item
            inventory_text += item.short_description()
        inventory_text = utils.newline(inventory_text, 2)
        inventory_text += self.print_equipped()
        return inventory_text

    def print_equipped(self):
        """returns string representation of equipped items"""
        equipped_text = utils.join_items(
            *[
                (type_.name.lower(), classes.all_items[item_name].short_description())
                for type_, item_name in self.equipped.items()
                if item_name
            ], is_description=True
        )
        return equipped_text  # .title() not sure about title

    def to_dict(self):
        return {
            "items": self.items,
            "max_items": self.max_items,
            "equipped": {type_.value: item_name for type_, item_name in self.equipped.items()},
        }

    def modifers(self):
        modifier_attack = 0
        modifier_defense = 0
        # TODO: make this a loop later
        weapon = self.get_equipped(classes.ItemType.WEAPON)[1]
        armor = self.get_equipped(classes.ItemType.ARMOR)[1]
        if weapon:
            modifier_attack += weapon.stats.attack
            modifier_defense += weapon.stats.defense
        if armor:
            modifier_attack += armor.stats.attack
            modifier_defense += armor.stats.defense
        return classes.Stats(attack=modifier_attack, defense=modifier_defense)

    commands = {
        # TODO: dont let player add anything to inventory
        "add": add,
        "remove": remove,
        "equip": equip,
        "unequip": unequip,
        "inventory": print_inventory,
        # TODO: command to view stats of an item
    }


class Player():
    """represents a player in the rpg"""

    def __init__(
        self, name,
        stats={
            "attack": 5, "defense": 5, "max_mana": 100, "mana": 100,
            "health": 100, "max_health": 100
        },
        room="village", fighting={}, inventory={}
    ):
        self.name = name
        self.stats = classes.Stats(alive=True, type_="player", **stats)
        self.room = room
        self.fighting = {
            enemy_name: classes.Enemy(**enemy_data)
            for enemy_name, enemy_data in fighting.items()
        }
        self.inventory = Inventory(**inventory)

    def get_id(self):
        return utils.get_key(players, self)

    def print_stats(self):
        """returns string representation of stats"""
        stats_list = []
        for stat_name, stat in self.stats.__dict__.items():
            # TODO: print modifiers from equipped items too
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
        rooms = classes.rooms
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
            "fighting": {
                enemy_name: enemy.to_dict()
                for enemy_name, enemy in self.fighting.items()
            },
            "inventory": self.inventory.to_dict(),
        }
        return player_dict

    def rest(self, commands):
        """rests player"""
        if classes.rooms[self.room].can_rest:
            self.stats.change_health("full")
            # TODO: change mana to max
            text = utils.join_items(
                "You feel well rested...",
                f"Your health is back up to {self.stats.health}!",
            )
        else:
            text = "You can't rest here!"

        return text

    def heal(self, commands):
        """heal the player with their tome"""
        tome_name, tome = self.inventory.get_equipped(classes.ItemType.TOME)
        if not tome_name:
            return "you do not have a tome equipped"
        if self.stats.mana < tome.stats.mana:
            return "You do not have enough mana to heal!"
        else:
            self.stats.mana -= tome.stats.mana
            self.stats.change_health(tome.stats.health)

            return f"You have been healed back up to {self.stats.health}"

    # TODO: merge with fight
    def attack(self, commands):
        """attacks an enemy"""
        text = ""

        if not self.fighting:
            return "You need to be in a fight!"

        enemy = random.choice(list(self.fighting.values()))
        enemy_name = utils.get_key(self.fighting, enemy)
        user_damage = self.modified_stats().attack
        damage_dealt = int(user_damage * (user_damage / enemy.stats.defense))

        multiplier = random.choice((1, -1))
        damage_dealt += int(multiplier * math.sqrt(damage_dealt / 2))
        enemy.stats.change_health(-damage_dealt)

        text += f"You dealt {damage_dealt} damage to {enemy_name}!\n"

        if enemy.stats.health <= 0:
            text += self.killed_enemy(enemy_name, enemy)

        else:
            # take damage
            damage_taken = int(enemy.stats.attack / self.modified_stats().defense)

            multiplier = random.choice((1, -1))
            damage_taken += int(multiplier * math.sqrt(damage_taken / 2))

            self.stats.change_health(-damage_taken)

            text += utils.join_items(
                f"{enemy_name} dealt {damage_taken} to you!",
                f"You have {self.stats.health} hp left",
                f"{enemy_name} has {enemy.stats.health} left!"
            )

            if self.stats.health <= 0:
                text += f"You were killed by {enemy_name}..."

                self.fighting = ""
                self.stats.change_health("full")

        return text

    def killed_enemy(self, enemy_name, enemy):
        """changes stuff based on enemy"""
        text = ""
        text += f"{enemy_name} is now dead!\n"

        xp_range = classes.rooms[self.room].xp_range
        xp_earned = random.randint(*xp_range)
        gold_earned = int(enemy.stats.max_health / 10) + random.randint(1, 10)

        text += f"You earned {xp_earned} xp and {gold_earned} gold!"
        self.stats.give_xp(xp_earned)
        self.stats.increase_balance(gold_earned)
        del self.fighting[enemy_name]

        return text

    def fight(self, commands):
        """starts a with an enemy"""
        text = ""
        room = classes.rooms[self.room]

        if not room.enemies_list:
            text = "There are no enemies here"

        elif self.fighting:
            text = f"You are already fighting {', '.join(self.fighting.keys())}!"

        else:
            enemy_name, enemy = room.generate_enemy()
            text += f"{enemy_name} has approached to fight!\n"
            text += enemy.stats.print_stats()
            self.fighting[enemy_name] = enemy
        return text

    def print_profile(self):
        profile_text = utils.join_items(
            ("name", self.name), ("id", self.get_id()),
            is_description=True,
        ) + self.stats.print_stats()
        return profile_text
    commands = {
        "rest": rest,
        "warp": warp,
        "attack": attack,
        "fight": fight,
        "heal": heal,
    }


players = {}
