import utils

class Stats():

    def __init__(
        alive=False, random_stats=True, type_=None,
        *, max_health=100, attack=5, defense=5, max_mana=100, level=1, xp=0, balance=0
        ):
        if alive:
            self.health = self.max_health = max_health
        if type_ == "player":
            self.mana = self.max_mana = max_mana
            self.lifetime_balance = self.balance = balance
            self.xp = xp
        if random_stats():
            attack, defense = generate_from_level()
        self.attack = attack
        self.defense = defense
        self.level = level

    def generate_from_level(self, level):
        # change this joseph
        attack = 5
        defense = 5
        return attack, defense

    def print_stats(self):
        pass


class Player():

    def __init__(self, name):
        self.name = name
        self.stats = Stats()
        self.room = "village"
        self.fighting = {}
        self.inventory = [None for i in range(8)]
        self.inventory[0:3] = [all_items["starter armor"], all_items["starter weapon"]]
        self.equipped = {"armor": 0, "weapon": 1}
        self.tome = "clarity"

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

        for item in items:
            item_name = utils.get_key(all_items, item)
            added_text = f"put {item_name} in slot {i}"
            if slot is not None:
                replaced_item_name = utils.get_key(all_items, self.inventory[slot])
                try:
                    self.inventory[slot] = item
                except IndexError:
                    return f"slot {slot} does not exist"
                return text + f"replacing {replaced_item_name}"
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = item
                    item_name = get_key(all_items, item)
                    return text
                return "there are no empy slots, specify a slot"
        return output_text

    def print_inventory(self):
        inventory_text = ""

        for item in self.inventory:
            inventory_text += item.description()
        return inventory_text

    def print_stats(self):
        return self.stats.print_stats()


class Enemy():

    def __init__():
        pass


class Item():

    rarities = ("common", "uncommon", "rare", "legendary")

    def __init__(self, type_, rarity=0, modifier="boring"):
        self.type_ = type_
        self.rarity = rarity
        self.modifier = modifier

    def description(self):
        return f"{Item.rarities[self.rarity]} {self.modifier} {get_key(all_items, self)}\n"

all_items = {
    "starter armor": Item("armor"),
    "starter weapon": Item("weapon"),
    "clarity tome": Item("tome")
}