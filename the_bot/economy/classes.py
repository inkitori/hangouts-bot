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
        self.prestige_confirm = 0
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
        userID = user.id_[0]

        player_pick = shop["picks"][self.items["pick"]]
        mined_amount = random.randint(*player_pick.mining_range)
        mined_amount += math.ceil(mined_amount * self.prestige / 100)
        mined_amount *= 2 ** self.prestige_upgrade

        self.change_balance(mined_amount)

        return f"{self.name}, you mined {mined_amount} Saber Dollars!"

    def buy(self, commands):
        """buys a item"""
        userID = user.id_[0]

        try:
            item_type = next(commands)
            item = next(commands)

            if item == "Top":
                if item_type not in self.data["shop"]:
                    conv.send_message(toSeg("That class doesn't exist!"))
                    return

                shopData = self.data["shop"][item_type]
                possible_items = []

                for possible_item in shopData:
                    if shopData[possible_item]["value"] > shopData[self.pick] and shopData[possible_item]["price"] <= self["balance"]:
                        possible_items.append(possible_item)

                if len(possible_items) == 0:
                    conv.send_message(toSeg("No possible item of that class you can purchase!"))
                    return

                else:
                    purchase = possible_items[-1]
                    userData[item_type] = shopData[purchase]["name"]
                    self.change_balance(purchase.price)

                    conv.send_message(toSeg("Successful purchase of the " + purchase + "!"))
                    return

            elif item_type not in self.data["shop"] or item not in self.data["shop"][item_type]:
                return "That item doesn't exist!"

            else:
                if self.balance < self.data["shop"][item_type][item]["price"]:
                    conv.send_message(toSeg("You don't have enough money for that!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] == self.data["shop"][item_type][item]["value"]:
                    conv.send_message(toSeg("You already have that pick!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] > self.data["shop"][item_type][item]["value"]:
                    return "You already have a pick better than that!"
                else:
                    self.data["users"][userID][item_type] = self.data["shop"][item_type][item]["name"]
                    self.data["users"][userID]["balance"] -= self.data["shop"][item_type][item]["price"]

                    return "Purchase successful!"

        except Exception as e:
            return "Format: /buy {type} {item}"
            print(e)

    def give(self, bot, event):
        """gives money to another user"""
        user, conv = getUserConv(bot, event)
        users = conv.users
        userID = user.id_[0]
        give_users = []

        try:
            give_user = event.text.split(' ', 1)[1]
            give_user = give_user.rsplit(' ', 1)[0]

            money = int(event.text.split()[-1])

            if userIn(self.ignore, user):
                conv.send_message(toSeg("You are an ignored user!"))
                return

            for u in users:
                if give_user in u.full_name:
                    give_users.append(u)

            if userID not in self.data["users"]:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif len(give_users) != 1:
                conv.send_message(toSeg("Error finding that user! Try /id_give instead."))
                return

            elif give_users[0].id_[0] not in self.data["users"]:
                conv.send_message(toSeg("That user has not registered!"))
                return

            elif give_users[0].id_[0] == user.id_[0]:
                conv.send_message(toSeg("That user is you!"))
                return

            elif money < 0:
                conv.send_message(toSeg("You can't give negative money!"))
                return

            elif self.data["users"][userID]["balance"] < money:
                conv.send_message(toSeg("You don't have enough money to do that!"))
                return

            else:
                self.data["users"][userID]["balance"] -= money
                self.data["users"][give_users[0].id_[0]]["balance"] += money
                self.data["users"][give_users[0].id_[0]]["lifetime_balance"] += money

                conv.send_message(toSeg("Successfully given " + str(money) + " Saber Dollars to " + give_users[0].full_name))
                conv.send_message(toSeg("That user now has " + str(self.data["users"][give_users[0].id_[0]]["balance"]) + " Saber Dollars"))

        except:
            conv.send_message(toSeg("Format: /give {user} {money}"))

    def id_give(self, bot, event):
        """gives money to another user"""
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        try:
            give_user = event.text.split()[1]
            give_money = int(event.text.split()[-1])

            if userIn(self.ignore, user):
                conv.send_message(toSeg("You are an ignored user!"))
                return

            if userID not in self.data["users"]:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif give_user not in self.data["users"]:
                conv.send_message(toSeg("That user has not registered!"))
                return

            elif userID == give_user:
                conv.send_message(toSeg("That user is you!"))
                return

            elif self.data["users"][userID]["balance"] < give_money:
                conv.send_message(toSeg("You don't have enough money to do that!"))
                return

            elif give_money < 0:
                conv.send_message(toSeg("You can't give negative money!"))
                return

            else:
                self.data["users"][userID]["balance"] -= give_money
                self.data["users"][give_user]["balance"] += give_money
                self.data["users"][give_user]["lifetime_balance"] += give_money
                conv.send_message(toSeg("Successfully given " + str(give_money) + " Saber Dollars to ID: " + str(give_user)))
                conv.send_message(toSeg("That user now has " + str(self.data["users"][give_user]["balance"]) + " Saber Dollars"))
        except:
            conv.send_message(toSeg("Format: /id_give {id} {money}"))

    def prestige(self, bot, event):
        """prestiges"""
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        try:
            if userID not in self.data["users"]:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            current_prestige = self.data["users"][userID]["prestige"]
            earned_prestige = math.trunc(self.data["users"][userID]["lifetime_balance"] / self.prestige_conversion)

            conv.send_message(toSeg(
                "You currently have " + str(current_prestige) + " prestige point(s). If you prestige, you will earn " +
                str(earned_prestige) + " more prestige point(s), or a " +
                str(earned_prestige) + "% bonus, but will lose all your money and items.")
                )
            conv.send_message(toSeg('Type "/prestige_confirm" if you really do wish to prestige.'))

            self.data["users"][userID]["prestige_confirm"] = 1

        except Exception:
            conv.send_message(toSeg("Something went wrong!"))

    def prestige_confirm(self, bot, event):
        """confirms prestige"""
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        userData = self.data["users"]

        try:
            if userID not in userData:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif not userData[userID]["prestige_confirm"]:
                return "You have to use /prestige before using this command!"
                return

            else:
                conv.send_message(toSeg("Prestiging"))
                userData[userID]["balance"] = 0
                userData[userID]["prestige"] += math.trunc(userData[userID]["lifetime_balance"] / self.prestige_conversion)
                userData[userID]["prestige_confirm"] = 0
                userData[userID]["lifetime_balance"] = 0
                userData[userID]["pick"] = "Copper Pick"

                utils.save(self.save_file, self.data)

                return "Successfully prestiged"

        except:
            conv.send_message(toSeg("Something went wrong!"))

    def prestige_upgrade_info(self, bot, event):
        """returns information about prestige"""
        user, conv = getUserConv(bot, event)
        userData = self.data["users"]
        userID = user.id_[0]

        if userID not in userData:
            conv.send_message(toSeg("You are not registered! Use /register"))
            return

        prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** userData[userID]["prestige_upgrade"])
        conv.send_message(toSeg("By prestiging, you will lose " + str(prestige_upgrade_cost) + " prestige."))

    def prestige_upgrade(self, bot, event):
        """upgrades prestige"""
        try:
            prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** self.prestige_upgrade)

            if self.prestige < prestige_upgrade_cost:
                return f"That costs {prestige_upgrade_cost} prestige, which you don't have enough of!"


            userData[userID]["prestige_upgrade"] += 1
            userData[userID]["prestige"] -= prestige_upgrade_cost
            self.data["users"][userID]["prestige_upgrade_confirm"] = 0

            with open(self.save_file, "w") as f:
                json.dump(self.data, f)

            conv.send_message(toSeg("Successfully upgraded prestige!"))

        except Exception as e:
            conv.send_message(toSeg("Something went wrong!"))
            print(e)

    def profile(self):
        """returns user profile"""
        profile_text = utils.join_items(
            f"Name: {self.name}",
            f"Balance: {self.balance}",
            f"Pick: {self.pick}",
            f"Prestige: {self.prestige}",
            f"Prestige Level: {self.prestige_level}",
            f"ID: {utils.get_key(self)}"
        )
        return profile_text
