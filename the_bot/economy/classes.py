"""
classes for economy game
"""
import utils
import math
import random


class Item():

    def __init__(self, type_, price, modifer="", mining_range=None):
        self.type_ = type_
        self.price = price
        self.modifer = modifer
        if self.type_ == "pick":
            self.mining_range = mining_range

    def name(self):
        """the name of the item"""
        return f"{self.modifer}{self.type_}".title().replace(" ", "_")


shop = {
    "picks": (
        Item("pick", 100, "tin"),
        Item("pick", 250, "iron"),
        Item("pick", 625, "lead"),
        Item("pick", 1565, "silver"),
        Item("pick", 3910, "tungsten"),
        Item("pick", 9775, "gold"),
        Item("pick", 24440, "platinum"),
        Item("pick", 61100, "molten"),
        Item("pick", 152750, "cobalt"),
        Item("pick", 381875, "palladium"),
        Item("pick", 954687, "mythril"),
        Item("pick", 2386717, "orichalcum"),
        Item("pick", 5966792, "adamantite"),
        Item("pick", 14916980, "titanium"),
        Item("pick", 37292450, "chlorophyte"),
        Item("pick", 93231125, "spectre"),
        Item("pick", 233077812, "luminite"),
    )
}


class EconomyUser():
    """class for users in economy"""

    prestige_conversion = 100000
    prestige_upgrade_base = 2000

    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.lifetime_balance = 0
        self.prestige = 0
        self.items = {"pick": 0}
        self.confirmed_prestige = False
        self.prestige_upgrade = 0

    def change_balance(self, money):
        """increases money"""
        self.balance += money
        if money > 0:
            self.lifetime_balance += money

    def balance(self):
        """returns balance"""
        return f"{self.name}, you currently have {self.balance} Saber Dollars!"

    def mine(self):
        """mines for saber dollars"""

        player_pick = shop["picks"][self.items["pick"]]
        mined_amount = random.randint(*player_pick.mining_range)
        mined_amount += math.ceil(mined_amount * self.prestige / 100)
        mined_amount *= 2 ** self.prestige_upgrade

        self.change_balance(mined_amount)

        return f"{self.name}, you mined {mined_amount} Saber Dollars!"

    def buy(self, commands):
        """buys a item"""
        try:
            item_type = next(commands)
            item = next(commands)

            if item == "top":
                if item_type not in self.shop:
                    return "That class doesn't exist!"

                shopData = self.shop[item_type]
                possible_items = []

                for possible_item in shopData:
                    if shopData[possible_item]["value"] > shopData[self.pick] and shopData[possible_item].price <= self.balance:
                        possible_items.append(possible_item)

                if len(possible_items) == 0:
                    return "No possible item of that class you can purchase!"

                else:
                    purchase = possible_items[-1]
                    self.items[item_type] = shopData[purchase].name()
                    self.change_balance(- purchase.price)

                    return "Successful purchase of the {purchase}!"

            elif item_type not in self.shop or item not in self.shop[item_type]:
                return "That item doesn't exist!"

            else:
                if self.balance < self.shop[item_type][item].price:
                    return "You don't have enough money for that!"
                elif self.shop[item_type][self.items[item_type]] == self.shop[item_type][item]:
                    return "You already have that pick!"
                elif self.shop[item_type][self.items[item_type]]["value"] > self.shop[item_type][item]["value"]:
                    return "You already have a pick better than that!"
                else:
                    self.items[item_type] = self.shop[item_type][item].name
                    self.change_balance(- self.shop[item_type][item].price)

                    return "Purchase successful!"

        except Exception as e:
            return "Format: /buy {type} {item}"
            print(e)

    def prestige(self):
        """prestiges"""
        output_text = ""
        earned_prestige = math.trunc(self.lifetime_balance / self.prestige_conversion)

        output_text += utils.join_items(
            f"You currently have {self.prestige} prestige point(s).",
            f"If you prestige, you will earn {earned_prestige} more prestige point(s), or a " +
            f"{earned_prestige}% bonus, but will lose all your money and items.",
            f"Type prestige_confirm if you really do wish to prestige."
        )

        self.confirmed_prestige = True

    def prestige_cancel(self):
        self.confirmed_prestige = False
        return "Prestige canceled"

    def prestige_confirm(self):
        """confirms prestige"""
        output_text = ""
        if not self.confirmed_prestige:
            output_text = "You have to use /prestige before using this command!"
        else:
            self.prestige_reset()
            output_text = "Successfully prestiged"

        return output_text

    def prestige_reset(self):
        self.balance = 0
        self.lifetime_balance = 0
        self.prestige = 0
        self.confirmed_prestige = False
        self.items = {"pick": 0}

    def prestige_upgrade_info(self):
        """returns information about prestige"""
        prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** self.prestige_upgrade)
        return f"By prestiging, you will lose {prestige_upgrade_cost} prestige."

    def prestige_upgrade(self, bot, event):
        """upgrades prestige"""
        prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** self.prestige_upgrade)

        if self.prestige < prestige_upgrade_cost:
            return f"That costs {prestige_upgrade_cost} prestige, which you don't have enough of!"

        self.prestige_upgrade += 1
        self.prestige -= prestige_upgrade_cost
        self.confirmed_prestige = False
        return "Successfully upgraded prestige!"

    def profile(self):
        """returns user profile"""
        profile_text = utils.join_items(
            f"Name: {self.name}",
            f"Balance: {self.balance}",
            f"Pick: {self.pick}",
            f"Prestige: {self.prestige}",
            f"Prestige Level: {self.prestige_level}",
            f"ID: {self.id()}"
        )
        return profile_text

    def id(self):
        return utils.get_key(users, self)
