class Player(Alive):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.other_stats = {"balance": 0, "lifetime balance": 0, "level": 1, "xp": 0}
        self.battle_stats = {"vitality": 100, "health": 100, "attack": 5, "defense": 5}
        self.room = "village"
        self.fighting = {}
        self.inventory = [None for i in range(8)]
        self.inventory[0:2] = [all_items["starter armor"], all_items["starter weapon"]]
        self.equipped = {"armor": 0, "weapon": 1}

    def add_to_inventory(item, slot=None):
        """
        puts an item into the first empty slot
        if a slot is specifed, uses that slot instead
        """
        text = f"put {item_name} in slot {i}"
        if slot is not None:
            replaced_item_name = get_key(RPGManager.all_items, self.inventory[slot])
            try:
                self.inventory[slot] = item
            except IndexError:
                return f"slot {slot} does not exist"
            return text + f"replacing {item_name}"
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                item_name = get_key(RPGManager.all_items, item)
                return text
            return "there are no empy slots, specify a slot"


class Enemy(Alive):

    def __init__():
        super().__init__()


class Item():

    rarities = ("common", "uncommon", "rare", "legendary")

    def __init__(type_, rarity=0, modifier="boring"):
        self.type_ = type_
        self.rarity = rarity
        self.modifier = modifier
        self.description = f"{Item.rarities[self.rarity]} {self.modifier} {get_key(RPGHandler.all_items, self)}\n"