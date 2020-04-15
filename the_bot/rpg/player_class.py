import utils
import sys
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
        self.equipped = equipped

    def add(self, commands):
        """
        puts an item into the inventory
        """
        item_name = next(commands)
        output_text = ""
        if not item_name:
            output_text = "you must pick an item"
        elif sum(self.items.values()) >= self.max_items:
            output_text = "your inventory is full, remove something first"
        # this still lets the player add anything if they know the name
        elif item_name not in RPG.all_items:
            output_text = "that item does not exist"
        else:
            # increments the value
            self.items[item_name] = utils.get_value(self.items, item_name, default=0) + 1
            output_text = f"added {item_name} to inventory"
        return output_text

    def remove(self, commands):
        item_name = next(commands)
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
        item_name = next(commands)
        if not item_name:
            output_text += "you must specify an item"
        elif item_name not in self.items:
            output_text += "you do not have that item"
        else:
            item_type = RPG.all_items[item_name].type_
            current_equipped_item = self.get_equipped(item_type)[0]
            if current_equipped_item == item_name:
                output_text += "you already equipped that"
            else:
                output_text += f"equipping {item_name} as {item_type}"
                self.equipped[item_type] = item_name
                if current_equipped_item:
                    output_text += f" replacing {current_equipped_item}"
        return output_text

    def unequip(self, commands):
        output_text = ""
        # accepts tiem name of type
        # uses redundant variables make code more readable
        name = type_ = next(commands)
        if not name:
            output_text = "you must specify an item name or type"
        elif type_ in classes.Item.types:
            if not self.equipped[type_]:
                output_text = "you do not have anything equipped of that type"
            else:
                current_equipped_item = self.equipped[type_]
                self.equipped[type_] = None
                output_text = f"unequipped {current_equipped_item} as {type_}"
        elif name in RPG.all_items:
            item_type = RPG.all_items[name].type_
            if self.equipped[item_type] != name:
                output_text = "that item is not equipped"
            else:
                self.equipped[item_type] = None
                output_text = f"unequipped {name} as {type_}"
        else:
            output_text = "invalid type or name"
        return output_text

    def get_equipped(self, type_):
        item_name = self.equipped[type_]
        item = RPG.all_items[item_name] if item_name else None
        return item_name, item

    def print_inventory(self, commands):
        """returns string representation of inventory"""
        inventory_text = ""
        # change to use utils.join_items
        for item_name, item_count in self.items.items():
            item = RPG.all_items[item_name]
            inventory_text += item.short_description()
        inventory_text = utils.newline(inventory_text, 2)
        inventory_text += self.print_equipped()
        return inventory_text

    def print_equipped(self):
        """returns string representation of equipped items"""
        equipped_text = utils.join_items(
            *[
                (type_, RPG.all_items[item_name].short_description())
                for type_, item_name in self.equipped.items()
                if item_name
            ], is_description=True
        )
        return equipped_text  # .title() not sure about title

    def to_dict(self):
        return self.__dict__

    def modifers(self):
        modifier_attack = 0
        modifier_defense = 0
        # make this a loop later
        weapon = self.get_equipped("weapon")[1]
        armor = self.get_equipped("armor")[1]
        if weapon:
            modifier_attack += weapon.stats.attack
            modifier_defense += weapon.stats.defense
        if armor:
            modifier_attack += armor.stats.attack
            modifier_defense += armor.stats.defense
        return classes.Stats(attack=modifier_attack, defense=modifier_defense)

    commands = {
        "add": add,
        "remove": remove,
        "equip": equip,
        "unequip": unequip,
        "inventory": print_inventory
    }


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
        self.fighting = {enemy_name: classes.Enemy(**enemy_data) for enemy_name, enemy_data in fighting.items()}
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

    def to_dict(self):
        player_dict = {
            "name": self.name,
            "stats": self.stats.to_dict(),
            "room": self.room,
            "fighting": {enemy_name: enemy.to_dict() for enemy_name, enemy in self.fighting.items()},
            "inventory": self.inventory.to_dict(),
        }
        return player_dict

    def rest(self, commands):
        """rests player"""
        if RPG.rooms[self.room].can_rest:
            self.stats.change_health("full")
            text = utils.join_items(
                "You feel well rested...",
                f"Your health is back up to {self.stats.health}!",
            )
        else:
            text = "You can't rest here!"

        return text

    def heal(self, commands):
        """heal the player with their tome"""
        tome_name, tome = self.inventory.get_equipped("tome")
        if not tome_name:
            return "you do not have a tome equipped"
        if self.stats.mana < tome.stats.mana:
            return "You do not have enough mana to heal!"
        else:
            self.stats.mana -= tome.stats.mana
            self.stats.change_health(tome.stats.health)

            return f"You have been healed back up to {self.stats.health}"

    def attack(self, commands):
        """attacks an enemy"""
        text = ""

        if not self.fighting:
            return "You need to be in a fight!"

        enemy = random.choice(list(self.fighting.values()))
        enemy_name = utils.get_key(self.fighting, enemy)
        user_damage = self.modified_stats().attack
        damage_dealt = user_damage * (user_damage / enemy.stats.defense)

        multiplier = random.choice((1, -1))
        damage_dealt += int(multiplier * math.sqrt(damage_dealt / 2))
        enemy.stats.change_health(- damage_dealt)

        text += f"You dealt {damage_dealt} damage to {enemy_name}!\n"

        if enemy.stats.health <= 0:
            text += self.killed_enemy(enemy_name, enemy)

        else:
            # take damage
            damage_taken = enemy.stats.attack / self.modified_stats().defense

            multiplier = random.choice((1, -1))
            damage_taken += int(multiplier * math.sqrt(damage_taken / 2))

            self.stats.change_health(- damage_taken)

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

        xp_range = RPG.rooms[self.room].xp_range
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
        room = RPG.rooms[self.room]

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
            ("name", self.name), ("id", self.id()),
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


class RPG():
    """the RPG"""

    all_items = classes.all_items
    players = {}
    rooms = classes.rooms
    enemies = classes.enemies
    help_text = "placeholder help text"

    def __init__(self):
        for item_name in self.all_items:
            if len(utils.clean(item_name)) > 1:
                print(f"invalid item name {item_name}, fix rpg.classes.all_items dict")
                sys.exit()
        for room_name in self.rooms:
            for enemy_name in self.rooms[room_name].enemies_list:
                if enemy_name not in self.enemies:
                    print(f"invalid enemy {enemy_name} in room {room_name}")

    def register(self, userID, commands):
        """registers a user in the game"""
        name = next(commands)
        if userID in self.players:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.players[userID] = Player(name=name)
        return "Successfully registered!"

    def profile(self, player, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_players = []

        for possible_player in self.players.values():
            if user_name in possible_player.name:
                possible_players.append(possible_player)
        if user_name.isdigit() and int(user_name) in self.players:
            possible_players.append(self.players[int(user_name)])
        elif user_name == "self":
            possible_players.append(player)
        if not possible_players:
            output_text += "No users go by that name!"

        elif len(possible_players) > 1:
            output_text += f"{len(possible_players)} player(s) go by that name:\n"

        for user in possible_players:
            output_text += user.print_profile()
        return utils.newline(output_text)

    def play_game(self, userID, commands):
        """runs functions based on user command"""
        command = next(commands)
        output_text = ""
        player = utils.get_value(self.players, userID)
        if command == "register":
            output_text = self.register(userID, commands)
        elif command == "help":
            output_text = self.help_text
        elif command in Inventory.commands:
            output_text = Inventory.commands[command](player.inventory, commands)
        elif command in Player.commands:
            output_text = Player.commands[command](player, commands)
        elif command == "profile":
            output_text = self.profile(player, commands)
        else:
            output_text = "invalid command"

        return output_text
