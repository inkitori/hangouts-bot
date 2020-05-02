import utils
import random
import copy
import math
import rpg.classes as classes


class Inventory:
    """player's inventory"""

    def __init__(self):
        self.items = {}
        self.max_items = 8
        self.equipped = {type_: None for type_ in classes.ItemType}

    def validate_item_name(self, item_name, modifier=None):
        if modifier is not None:
            if not modifier:
                return "you must pick an item"
            elif modifier not in [item_modifier.name.lower() for item_modifier in classes.ItemModifer]:
                return "that modifier does not exist"
        if not item_name:
            return "that is not a valid item name"
        elif item_name not in classes.all_items:
            return "that item does not exist"
        return "valid"

    def add(self, commands):
        """
        puts an item into the inventory
        """
        # input validation
        item_name = commands.send("remaining")
        item_is_valid = self.validate_item_name(item_name)
        if item_is_valid != "valid":
            return item_is_valid

        if sum([item.count for item in self.items.values()]) >= self.max_items:
            return "your inventory is full, remove something first"

        # TODO: this still lets the player add anything if they know the name
        item = classes.all_items[item_name]
        if item.full_name() in self.items:
            self.items[item.full_name()].count += 1
        else:
            item = copy.copy(item)
            item.stats = copy.deepcopy(item.stats)
            self.items[item.full_name()] = item
            item.count = 1

        return f"added {item_name} to inventory"

    def remove(self, commands):
        # input validation
        modifier = next(commands)
        item_name = commands.send("remaining")
        item_is_valid = self.validate_item_name(item_name, modifier)
        if item_is_valid != "valid":
            return item_is_valid

        full_item = utils.join_items(modifier, item_name, separator=' ')

        if full_item not in self.items:
            return "you do not have that item"

        item = self.items[full_item]
        if (full_item in self.equipped and item.count == 1):
            return "you must unequip that item first"

        item.count -= 1
        if item.count == 0:
            del self.items[full_item]
        return f"1 {full_item.title()} removed from inventory"

    def equip(self, commands):
        """equips an item"""
        output_text = ""
        modifier = next(commands)
        item_name = commands.send("remaining")
        full_name = utils.join_items(modifier, item_name, separator=' ')

        item_is_valid = self.validate_item_name(item_name, modifier)
        if item_is_valid != "valid":
            return item_is_valid

        if full_name not in self.items:
            return "you do not have that item"

        item_type = classes.all_items[item_name].type_
        current_equipped_item = self.get_equipped(item_type)[0]
        if current_equipped_item == item_name:
            return "you already equipped that"
        output_text += f"equipping {item_name} as {item_type.name.lower()}"
        self.equipped[item_type] = full_name
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
            modifier, *item_name = name.split()
            item_name = ''.join(item_name)
            item_is_valid = self.validate_item_name(item_name, modifier)
            if item_is_valid != "valid":
                return item_is_valid

        if type_:
            if not self.equipped[type_]:
                output_text = "you do not have anything equipped of that type"
            else:
                current_equipped_item = self.equipped[type_]
                self.equipped[type_] = None
                output_text = f"unequipped {current_equipped_item} as {type_.name.lower()}"

        elif name in self.equipped.values():
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
        item = self.items[item_name] if item_name else None
        return item_name, item

    def print_inventory(self, commands):
        """returns string representation of inventory"""
        if not self.items:
            return "you dont have anything in your inventory"
        inventory_text = ""  # TODO: print # of full slots
        inventory_text += utils.join_items(
            ("inventory", *[
                f"{item.description()} x{item.count}"
                for item in self.items.values()
            ]), newlines=2, description_mode="long"
        )
        if not [item for item in self.equipped.values() if item is not None]:
            inventory_text += "you don't have anything equipped, use equip to equip something"
        else:
            inventory_text += self.print_equipped()
        return inventory_text

    def print_equipped(self):
        """returns string representation of equipped items"""
        return utils.join_items(
            ("equipped", *[
                utils.description(type_.name.lower(), item_name)
                for type_, item_name in self.equipped.items()
                if item_name
            ]), description_mode="long"
        )

    def modifers(self):
        modifier_attack = 0
        modifier_defense = 0
        # TODO: make this a loop later
        weapon = self.get_equipped(classes.ItemType.WEAPON)[1]
        armor = self.get_equipped(classes.ItemType.ARMOR)[1]
        if weapon:
            modifier_attack += utils.default(weapon.stats.attack, 0)
            modifier_defense += utils.default(weapon.stats.defense, 0)
        if armor:
            modifier_attack += utils.default(armor.stats.attack, 0)
            modifier_defense += utils.default(armor.stats.defense, 0)
        return classes.Stats(attack=modifier_attack, defense=modifier_defense)

    commands = {
        # TODO: dont let player add anything to inventory
        "add": add,
        "remove": remove,
        "equip": equip,
        "unequip": unequip,
        "inventory": print_inventory,
        # TODO: details {item_name} command to view stats of an item
    }


class Player:
    """represents a player in the rpg"""

    def __init__(self, name):
        # TODO: move pass as arguments in stats and get rid of the dict
        stats = {
            "attack": 5, "defense": 5, "max_mana": 100, "mana": 100,
            "health": 100, "max_health": 100, "level": 1, "xp": 0,
            "balance": 0, "lifetime_balance": 0,
        }
        self.name = name
        self.stats = classes.Stats(**stats)
        self.room = "village"
        self.fighting = {}
        self.args = {"autofight": False, "heal_percent": 50}
        self.inventory = Inventory()

    def get_id(self):
        return utils.get_key(players, self)

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

        elif room == self.room:
            output_text = "You are already in that room!"
        else:
            self.room = room
            output_text = "Successfully warped!"
        return output_text

    def rest(self, commands):
        """rests player"""
        if classes.rooms[self.room].can_rest:
            self.stats.health = "full"
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
            self.stats.health += tome.stats.health

            text = utils.newline(
                f"You have been healed back up to {self.stats.health}")

            if self.fighting:
                enemy = random.choice(list(self.fighting.values()))
                text += enemy.attack(self)

            return text

    # TODO: merge with fight
    def attack(self, commands):
        """attacks an enemy"""
        text = ""

        if not self.fighting:
            return "You need to be in a fight!"

        enemy = random.choice(list(self.fighting.values()))
        enemy_name = utils.get_key(self.fighting, enemy)
        player_damage = self.modified_stats().attack + self.stats.attack
        damage_dealt = round(
            player_damage * (player_damage / enemy.stats.defense), 1)

        multiplier = random.choice((1, -1))
        damage_dealt += round(multiplier * math.sqrt(damage_dealt / 2), 1)
        damage_dealt = round(damage_dealt, 1)
        enemy.stats.health -= damage_dealt
        text += utils.newline(
            f"You dealt {damage_dealt} damage to {enemy_name}!")

        if enemy.stats.health <= 0:
            text += self.killed_enemy(enemy_name, enemy)

        else:
            # take damage
            print(enemy_name)
            text += enemy.attack(self)

            if self.stats.health <= 0:
                text += self.died(enemy_name)

        return text

    def died(self, cause):
        text = utils.join_items(
            f"You were killed by {cause}...",
            "You woke up back in the village"
        )
        self.fighting = {}
        self.stats.health = "full"
        self.warp("village" for _ in range(1))
        return text

    def killed_enemy(self, enemy_name, enemy):
        """changes stuff based on enemy"""
        text = ""
        text += f"{enemy_name} is now dead!\n"

        xp_earned = enemy.level ** 2
        gold_earned = int(enemy.stats.max_health / 10) + random.randint(1, 10)

        text += f"You earned {xp_earned} xp and {gold_earned} gold!"
        self.stats.give_xp(xp_earned)
        self.stats.increase_balance(gold_earned)
        del self.fighting[enemy_name]

        return text

    def fight(self, commands):
        """starts a with an enemy"""
        room = classes.rooms[self.room]

        if not room.enemies_list:
            return "There are no enemies here"
        elif self.fighting:
            return f"You are already fighting {', '.join(self.fighting.keys())}!"

        enemy_name, enemy = room.generate_enemy()
        self.fighting[enemy_name] = enemy

        if self.args["autofight"]:
            return self.autofight(enemy_name, enemy)
        else:
            return utils.join_items(
                f"{enemy_name} has approached to fight!",
                enemy.stats.print_stats(),
                separator="\n\t"
            )

    def autofight(self, enemy_name):
        while True:
            # this might get deleted so leave it alone for now
            pass

    def set_(self, commands):
        arg = next(commands)
        value = next(commands)

        # input validation
        if arg not in self.args:
            return "That is not a valid arg!"
        elif not arg:
            return "you must provide an arg"
        elif not value:
            return "you must provide a value"

        elif isinstance(self.args[arg], bool):
            value = value[0]
            if value in ("t", "y"):
                self.args[arg] = True

            elif value in ("f", "n"):
                self.args[arg] = False
            else:
                # TODO make this error a template
                return f"invalid value {value} for boolean arg {arg}, use true/false"

        elif isinstance(self.args[arg], int):
            if value.isdigit():
                self.args[arg] = int(value)
            else:
                return f"invalid value {value} for integer arg {arg}, use an integer"

        return f"Successfully set {arg} to {self.args[arg]}"

    def profile(self):
        # TODO: change to use description_mode="long" by changing print_stats to have a lsit arg
        profile_text = utils.join_items(
            ("name", self.name), ("id", self.get_id()),
            description_mode="short", separator="\n\t"
        )
        return utils.join_items(
            profile_text, self.stats.print_stats(self.inventory.modifers()),
            separator="\n\t"
        )

    commands = {
        "rest": rest,
        "warp": warp,
        "attack": attack,
        "fight": fight,
        "heal": heal,
        "set": set_,
        # TODO: flee command to leave a fight (penalty for fleeing?)
    }


players = {}
parties = {}
