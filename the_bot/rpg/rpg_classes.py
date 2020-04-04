import utils

class Stats():

    def __init__(
        self, alive=False, random_stats=True, type_=None,
        *, max_health=100, attack=5, defense=5, max_mana=100, level=1, xp=0, balance=0
        ):
        if alive:
            self.health = self.max_health = max_health
        if type_ == "player":
            self.mana = self.max_mana = max_mana
            self.lifetime_balance = self.balance = balance
            self.xp = xp
        if random_stats():
            attack, defense = self.generate_from_level(level)
        self.attack = attack
        self.defense = defense
        self.level = level

    def generate_from_level(self, level):
        # change this joseph
        attack = round(5 * level ** 1.8)
        defense = round(5 * level ** 1.5)
        health = round(100 * level ** 2)
        return attack, defense, health

    def print_stats(self):
        pass

    def next_level_xp(self):
        return round(4 * (((self.level + 1) ** 4) / 5))

    def print_level_xp(self):
        return f"LVL: {self.level} | {self.xp} / {self.next_level_xp()}"

    def give_xp(self, xp_earned):
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


class Player():

    def __init__(self, name):
        self.name = name
        self.stats = Stats(True, False, "player")
        self.room = "village"
        self.fighting = {}
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
            added_text = f"put {item_name} in slot {i}"
            if slot is not None:
                replaced_item_name = utils.get_key(all_items, self.inventory[slot])
                try:
                    self.inventory[slot] = item_name
                except IndexError:
                    return f"slot {slot} does not exist"
                return text + f"replacing {replaced_item_name}"
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = item
                    output_text += utils.newline(added_text)
                output_text += "there are no empy slots, specify a slot"
        return output_text

    def print_inventory(self):
        inventory_text = ""

        for item_name in self.inventory:
            inventory_text += all_items[item_name].description()
        return inventory_text

    def print_stats(self):
        return self.stats.print_stats()

    def print_equipped(self):
        equipped = ""

        for type_, index in self.equipped.items():
            item = all_items[self.inventory[index]]
            equipped += f"{type_}: {item.description()}"

        return equipped.title()


class Enemy():

    def __init__():
        # ??
        self.atk = atk
        self.def = def
        self.hp = hp

class room


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
