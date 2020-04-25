"""
classes for economy game
"""
import utils
import math
import random


class Item():
    """items"""
    prices = {
        "pick": (
            0, 100, 250, 625, 1565, 3910, 9775, 24440, 61100, 152750, 381875, 954687,
            2386717, 5966792, 14916980, 37292450, 93231125, 233077812,
        ),
    }
    modifiers = {
        "pick": (
            "copper", "tin", "iron", "lead", "silver", "tungsten", "gold", "platinum", "molten",
            "cobalt", "palladium", "mythril", "orichalcum", "adamantite", "titanium",
            "chlorophyte", "spectre", "luminite",
        ),
    }

    def __init__(self, type_, price, modifer="", level=0):
        self.type_ = type_
        self.price = price
        self.modifer = modifer
        self.level = level
        if self.type_ == "pick":
            self.mining_range = self.generate_mining(level)

    def name(self):
        """the name of the item"""
        return f"{self.modifer} {self.type_}"

    def generate_mining(self, level):
        return (level + 2) ** 2 // 2, (level + 2) ** 2


def generate_items(type_):
    max_possible_items = min(len(Item.modifiers[type_]), len(Item.prices[type_]))
    return [
        Item(type_, Item.prices[type_][level], Item.modifiers[type_][level], level)
        for level in range(max_possible_items)
    ]


shop_items = {
    "pick": generate_items("pick")
}


class EconomyUser():
    """class for users in economy"""

    prestige_conversion = 100000
    prestige_upgrade_base = 2000

    def __init__(
        self, name, balance=0, lifetime_balance=0, items={"pick": 0},
        prestige=0, prestige_upgrade=0, confirmed_prestige=False, confirmed_upgrade=False
    ):
        self.name = name
        self.balance = balance
        self.lifetime_balance = lifetime_balance
        self.prestige = prestige
        self.items = items
        self.confirmed_prestige = False
        self.confirmed_upgrade = False
        self.prestige_upgrade = prestige_upgrade

    def change_balance(self, money):
        """increases money"""
        self.balance += money
        if money > 0:
            self.lifetime_balance += money

    def balance(self):
        """returns balance"""
        return f"{self.name}, you currently have {self.balance} Saber Dollars!"

    def mine(self, commands):
        """mines for saber dollars"""

        player_pick = self.get_item("pick")
        mined_amount = random.randint(*player_pick.mining_range)
        mined_amount += math.ceil(mined_amount * self.prestige / 100)
        mined_amount *= 2 ** self.prestige_upgrade

        self.change_balance(mined_amount)

        return f"{self.name}, you mined {mined_amount} Saber Dollars!"

    def buy(self, commands):
        """buys a item"""
        modifier = next(commands)
        item_type = next(commands)

        if modifier == "top":
            if item_type not in shop_items:
                return "That class doesn't exist!"

            possible_items = [
                item for item in shop_items[item_type]
                if item.level > self.items[item_type]
                and item.price <= self.balance
            ]

            if not possible_items:
                return "No possible item of that type you can purchase!"

            purchase = possible_items[-1]
            self.items[item_type] = shop_items[item_type].index(purchase)
            self.change_balance(- purchase.price)

            return f"Successful purchase of the {purchase.name}!"

        elif item_type not in shop_items or modifier not in Item.modifiers[item_type]:
            return "That item doesn't exist!"

        else:
            item_index = Item.modifiers[item_type].index(modifier)
            item = shop_items[item_type][item_index]
            if self.balance < item.price:
                return "You don't have enough money for that!"
            elif item_index == self.items[item_type]:
                return "You already have that item!"
            elif self.get_item("pick").level > item.level:
                return "You already have a pick better than that!"
            else:
                self.items[item_type] = item_index
                self.change_balance(- item.price)

                return "Purchase successful!"

    def prestige_action(self, commands):
        """gives prestige information"""
        output_text = ""
        earned_prestige = math.trunc(self.lifetime_balance / self.prestige_conversion)
        if self.confirmed_prestige:
            self.balance = 0
            self.lifetime_balance = 0
            self.confirmed_prestige = False
            self.confirmed_upgrade = False
            self.items = {"pick": 0}
            self.prestige += earned_prestige
            output_text = "Successfully prestiged"
        else:
            self.confirmed_prestige = True
            output_text += utils.join_items(
                f"You currently have {self.prestige} prestige point(s).",
                f"If you prestige, you will earn {earned_prestige} more prestige point(s), or a " +
                f"{earned_prestige}% bonus, but will lose all your money and items.",
                f"Use prestige again if you really do wish to prestige."
            )
        return output_text

    def prestige_upgrade_action(self, commands):
        """upgrades prestige"""
        output_text = ""
        prestige_upgrade_cost = math.floor(
            self.prestige_upgrade_base * 2.5 ** self.prestige_upgrade
        )
        if self.confirmed_upgrade:
            if self.prestige < prestige_upgrade_cost:
                output_text += f"That costs {prestige_upgrade_cost} prestige, which you don't have!"
            else:
                self.prestige_upgrade += 1
                self.prestige -= prestige_upgrade_cost
                output_text += "Successfully upgraded prestige!"
        else:
            output_text += utils.join_items(
                f"By upgrading, you will lose {prestige_upgrade_cost} prestige.",
                f"Use prestige_upgrade again if you really do wish to upgrade.",
            )
            self.confirmed_upgrade = True
        return output_text

    def profile(self):
        """returns user profile"""
        profile_text = utils.join_items(
            f"name: {self.name}",
            f"balance: {self.balance}",
            f"pick: {self.get_item('pick').name()}",
            f"prestige: {self.prestige}",
            f"prestige level: {self.prestige_upgrade}",
            f"id: {self.get_id()}"
        )
        return utils.newline(profile_text).title()

    def give(self, commands):
        """gives money to another user"""
        # input validation
        reciveing_user = next(commands)
        money = next(commands)
        if not reciveing_user:
            return "You must specfiy a user or ID"
        elif not money:
            return "You must specify an amount"
        elif not money.isdigit():
            return "You must give an integer amount of Saber Dollars"

        money = int(money)
        # get the user
        for user in users.values():
            if reciveing_user == user.name:
                reciveing_user = user
                break
        if reciveing_user.isdigit() and int(reciveing_user) in users:
            reciveing_user = users[int(reciveing_user)]

        # check user is valid
        if reciveing_user.get_id() not in users:
            return "That user has not registered!"
        elif reciveing_user.get_id() == self.get_id():
            return "That user is you!"

        # check money is valid
        if money < 0:
            return "You can't give negative money!"
        elif self.balance < money:
            return "You don't have enough money to do that!"

        self.change_balance(-money)
        reciveing_user.change_balance(money)

        return utils.join_items(
            f"Successfully given {money} Saber Dollars to {reciveing_user.name}.",
            f"{reciveing_user.name} now has {reciveing_user.balance} Saber Dollars."
        )

    def get_id(self):
        return utils.get_key(users, self)

    def get_item(self, type_):
        return shop_items[type_][self.items[type_]]

    commands = {
        "mine": mine,
        "buy": buy,
        "prestige": prestige_action,
        "prestige_upgrade": prestige_upgrade_action,
        "give": give,
    }


users = {}
