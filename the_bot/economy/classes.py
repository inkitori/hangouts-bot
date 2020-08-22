"""
classes for economy game
"""
import utils
import math
import random


class Item:
    """items"""
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

    @staticmethod
    def generate_items(type_, modifiers, prices):
        return [
            Item(type_, *data, level)
            for level, data in enumerate(zip(prices, modifiers))
        ]


class EconomyPlayer:
    """class for players in economy"""

    PRESTIGE_CONVERSION = 100000
    PRESTIGE_UPGRADE_BASE = 2000

    def __init__(self, id_, name, manager):
        self.id_ = id_
        self.name = name
        self.balance = 0
        self.lifetime_balance = 0
        self.prestige = 0
        self.items = {"pick": "copper"}
        self.confirmed_prestige = False
        self.confirmed_upgrade = False
        self.prestige_upgrade = 0
        self.manager = manager

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
        item = self.manager.get_item(modifier, item_type)
        if type(item) == str:
            return item

        if self.balance < item.price:
            return "You don't have enough money for that!"
        elif item.modifer == self.items[item_type]:
            return "You already have that item!"
        elif self.get_item(item_type).level > item.level:
            return "You already have a item better than that!"
        else:
            self.items[item_type] = modifier
            self.change_balance(- item.price)
            return "Purchase successful!"

    def give(self, commands):
        """gives money to another player"""
        # input validation
        receiving_player = next(commands)
        money = next(commands)
        if not money:
            return "You must specify an amount"
        elif not money.isdigit():
            return "You must give an integer amount of Saber Dollars"

        money = int(money)
        # get the player
        receiving_player = self.manager.get_player(receiving_player)
        if type(receiving_player) == str:
            return receiving_player
        if receiving_player.id_ == self.id_:
            return "That player is you!"

        # check money is valid
        if money < 0:
            return "You can't give negative money!"
        elif self.balance < money:
            return "You don't have enough money to do that!"

        self.change_balance(-money)
        receiving_player.change_balance(money)

        return utils.join_items(
            f"Successfully given {money} Saber Dollars to {receiving_player.name}.",
            f"{receiving_player.name} now has {receiving_player.balance} Saber Dollars."
        )

    def prestige_action(self, commands):
        """gives prestige information"""
        output_text = ""
        earned_prestige = math.trunc(
            self.lifetime_balance / EconomyPlayer.PRESTIGE_CONVERSION)
        if self.confirmed_prestige:
            self.balance = 0
            self.lifetime_balance = 0
            self.confirmed_prestige = False
            self.confirmed_upgrade = False
            self.items = {"pick": "copper"}
            self.prestige += earned_prestige
            output_text = "Successfully prestiged"
        else:
            self.confirmed_prestige = True
            output_text += utils.join_items(
                f"You currently have {self.prestige} prestige point(s).",
                f"If you prestige, you will earn {earned_prestige} more prestige point(s), or a " +
                f"{earned_prestige}% bonus, but will lose all your money and items.",
                "Use prestige again if you really do wish to prestige."
            )
        return output_text

    def prestige_upgrade_action(self, commands):
        """upgrades prestige"""
        output_text = ""
        prestige_upgrade_cost = math.floor(
            EconomyPlayer.PRESTIGE_UPGRADE_BASE * 2.5 ** self.prestige_upgrade
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
        """returns player profile"""
        profile_text = utils.join_items(
            f"name: {self.name}",
            f"balance: {self.balance}",
            f"pick: {self.get_item('pick').name()}",
            f"prestige: {self.prestige}",
            f"prestige level: {self.prestige_upgrade}",
            f"id: {self.id_}",
            separator="\n\t"
        )
        return profile_text.title()

    def get_item(self, item_type):
        return self.manager.get_item(self.items[item_type], item_type)

    commands = {
        "mine": mine,
        "prestige": prestige_action,
        "prestige_upgrade": prestige_upgrade_action,
        "give": give,
        "buy": buy,
    }
