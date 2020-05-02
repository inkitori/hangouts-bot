"""
inventory
"""
import rpg.classes as classes
import copy
import utils


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
            elif modifier not in [
                item_modifier.name.lower()
                for item_modifier in classes.ItemModifer
            ]:
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
        full_name = utils.join_items(
            modifier, item_name, separator=' ', newlines=0)

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
        inventory_text = f""  # TODO: print # of full slots
        inventory_text += utils.join_items(
            ("inventory", *[
                f"{item.get_description()} x{item.count}"
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
