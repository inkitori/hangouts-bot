"""
economy for bot
"""
import utils


class EconomyUser():

    prestige_conversion = 100000
    prestige_upgrade_base = 2000

    def __init__(self):

        if cooldown(self.cooldowns, user, event, 5):
            return

        if userID in self.data["users"]:
            conv.send_message(toSeg("You are already registered!"))
            return

        try:
            self.data["users"][userID] = user
            self.data["users"][userID] = {}
            self.data["users"][userID]["balance"] = 0
            self.data["users"][userID]["total_balance"] = 0
            self.data["users"][userID]["prestige"] = 0
            self.data["users"][userID]["pick"] = "Copper Pick"
            self.data["users"][userID]["name"] = user.full_name
            self.data["users"][userID]["prestige_confirm"] = 0
            self.data["users"][userID]["prestige_upgrade"] = 0

            with open(self.save_file, "w") as f:
                json.dump(self.data, f)

            conv.send_message(toSeg("Successfully registered!"))
        except Exception as e:
            conv.send_message(toSeg("Failed to register!"))
            print(e)

    def balance(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        if userID not in self.data["users"]:
            conv.send_message(toSeg("You are not registered! Use /register"))
            return

        try:
            balance = self.data["users"][userID]["balance"]
            conv.send_message(toSeg(user.full_name + ", you currently have " + str(balance) + " Saber Dollars!"))
        except Exception as e:
            conv.send_message(toSeg("Failed to retrieve balance info!"))
            print(e)

    def mine(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if userID not in self.data["users"]:
            conv.send_message(toSeg("You are not registered! Use /register"))
            return

        i = cooldown(self.cooldowns, user, event, 4)
        if i:
            conv.send_message(toSeg("On cooldown. Please wait " + str(i) + " second(s)."))
            return

        try:
            playerPick = self.data["shop"]["pick"][self.data["users"][userID]["pick"]]
            mined_amt = random.randint(playerPick["range"][0], playerPick["range"][1])
            mined_amt += math.ceil(mined_amt * self.data["users"][userID]["prestige"] / 100)
            mined_amt *= 2 ** self.data["users"][userID]["prestige_upgrade"]

            self.data["users"][userID]["balance"] += mined_amt
            self.data["users"][userID]["total_balance"] += mined_amt

            conv.send_message(toSeg(user.full_name + ", you mined " + str(mined_amt) + " Saber Dollars!"))

            with open(self.save_file, "w") as f:
                json.dump(self.data, f)

        except Exception as e:
            conv.send_message(toSeg("Failed to mine!"))
            print(e)

    def buy(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            item_type = event.text.split()[1].lower()
            item = event.text.split(' ', 2)[2].strip().lower().title()

            if userID not in self.data["users"]:
                conv.send_message(toSeg("You are not registered!  Use /register"))
                return

            elif item == "Top":
                if item_type not in self.data["shop"]:
                    conv.send_message(toSeg("That class doesn't exist!"))
                    return

                else:
                    shopData = self.data["shop"][item_type]
                    userData = self.data["users"][userID]
                    possible_items = []

                    for possible_item in shopData:
                        if shopData[possible_item]["value"] > shopData[userData["pick"]]["value"] and shopData[possible_item]["price"] <= userData["balance"]:
                            possible_items.append(possible_item)

                    if len(possible_items) == 0:
                        conv.send_message(toSeg("No possible item of that class you can purchase!"))
                        print("test")
                        return

                    else:
                        purchase = possible_items[-1]
                        userData[item_type] = shopData[purchase]["name"]
                        userData["balance"] -= shopData[purchase]["price"]

                        with open(self.save_file, "w") as f:
                            json.dump(self.data, f)

                        conv.send_message(toSeg("Successful purchase of the " + purchase + "!"))
                        return

            elif item_type not in self.data["shop"] or item not in self.data["shop"][item_type]:
                conv.send_message(toSeg("That item doesn't exist!"))
                return
            else:
                if self.data["users"][userID]["balance"] < self.data["shop"][item_type][item]["price"]:
                    conv.send_message(toSeg("You don't have enough money for that!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] == self.data["shop"][item_type][item]["value"]:
                    conv.send_message(toSeg("You already have that pick!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] > self.data["shop"][item_type][item]["value"]:
                    conv.send_message(toSeg("You already have a pick better than that!"))
                    return
                else:
                    self.data["users"][userID][item_type] = self.data["shop"][item_type][item]["name"]
                    self.data["users"][userID]["balance"] -= self.data["shop"][item_type][item]["price"]

                    with open(self.save_file, "w") as f:
                        json.dump(self.data, f)

                    conv.send_message(toSeg("Purchase successful!"))
        except Exception as e:
            conv.send_message(toSeg("Format: /buy {type} {item}"))
            print(e)

    def give(self, bot, event):
        user, conv = getUserConv(bot, event)
        users = conv.users
        userID = user.id_[0]
        give_users = []

        try:
            arg1 = event.text.split(' ', 1)[1]
            arg1 = arg1.rsplit(' ', 1)[0]

            arg2 = int(event.text.split()[-1])

            if userIn(self.ignore, user):
                conv.send_message(toSeg("You are an ignored user!"))
                return

            for u in users:
                if arg1 in u.full_name:
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

            elif arg2 < 0:
                conv.send_message(toSeg("You can't give negative money!"))
                return

            elif self.data["users"][userID]["balance"] < arg2:
                conv.send_message(toSeg("You don't have enough money to do that!"))
                return

            else:
                self.data["users"][userID]["balance"] -= arg2
                self.data["users"][give_users[0].id_[0]]["balance"] += arg2
                self.data["users"][give_users[0].id_[0]]["total_balance"] += arg2

                with open(self.save_file, "w") as f:
                    json.dump(self.data, f)

                conv.send_message(toSeg("Successfully given " + str(arg2) + " Saber Dollars to " + give_users[0].full_name))
                conv.send_message(toSeg("That user now has " + str(self.data["users"][give_users[0].id_[0]]["balance"]) + " Saber Dollars"))

        except:
            conv.send_message(toSeg("Format: /give {user} {money}"))

    def id_give(self, bot, event):
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
                self.data["users"][give_user]["total_balance"] += give_money
                with open(self.save_file, "w") as f:
                    json.dump(self.data, f)
                conv.send_message(toSeg("Successfully given " + str(give_money) + " Saber Dollars to ID: " + str(give_user)))
                conv.send_message(toSeg("That user now has " + str(self.data["users"][give_user]["balance"]) + " Saber Dollars"))
        except:
            conv.send_message(toSeg("Format: /id_give {id} {money}"))

    def profile(self, bot, event):
        user, conv = getUserConv(bot, event)
        dataUsers = self.data["users"]

        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            if len(event.text.split()) > 1:
                name = event.text.split(' ', 1)[1]
                possible_users = []

                for user in self.data["users"]:
                    if name in self.data["users"][user]["name"]:
                        possible_users.append(user)

                if len(possible_users) == 0:
                    conv.send_message(toSeg("No users go by that name!"))
                    return

                elif len(possible_users) > 1:
                    conv.send_message(toSeg(str(len(possible_users)) + " possible user(s) go by that name:\n"))

                    for user in possible_users:
                        conv.send_message(toSeg(
                            "**Name:** " + dataUsers[user]["name"] + '\n' +  # multiple users
                            "**Balance:** " + str(dataUsers[user]["balance"]) + '\n' +
                            "**Pick:** " + dataUsers[user]["pick"] + '\n' +
                            "**Prestige:** " + str(dataUsers[user]["prestige"]) + '\n' +
                            "**Prestige Level:** " + str(dataUsers[user]["prestige_upgrade"]) + '\n' +
                            "**ID:** " + user + '\n\n')
                        )
                else:
                    conv.send_message(toSeg(
                        "**Name:** " + dataUsers[possible_users[0]]["name"] + '\n' +  # single user
                        "**Balance:** " + str(dataUsers[possible_users[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[possible_users[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[possible_users[0]]["prestige"]) + '\n' +
                        "**Prestige Level:** " + str(dataUsers[possible_users[0]]["prestige_upgrade"]) + '\n' +
                        "**ID:** " + possible_users[0])
                    )

            else:
                if user.id_[0] in self.data["users"]:
                    conv.send_message(toSeg(
                        "**Name:** " + self.data["users"][user.id_[0]]["name"] + '\n' +  # no args
                        "**Balance:** " + str(self.data["users"][user.id_[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[user.id_[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[user.id_[0]]["prestige"]) + '\n' +
                        "**Prestige Level:** " + str(dataUsers[user.id_[0]]["prestige_upgrade"]) + '\n' +
                        "**ID:** " + user.id_[0])
                    )
        except Exception as e:
            conv.send_message(toSeg("Failed to retrieve user info!"))
            print(e)

    def prestige(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        try:
            if userID not in self.data["users"]:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            current_prestige = self.data["users"][userID]["prestige"]
            earned_prestige = math.trunc(self.data["users"][userID]["total_balance"] / self.prestige_conversion)

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
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        userData = self.data["users"]

        try:
            if userID not in userData:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif not userData[userID]["prestige_confirm"]:
                conv.send_message(toSeg('You have to use "/prestige" before using this command!'))
                return

            else:
                conv.send_message(toSeg("Prestiging"))
                userData[userID]["balance"] = 0
                userData[userID]["prestige"] += math.trunc(userData[userID]["total_balance"] / self.prestige_conversion)
                userData[userID]["prestige_confirm"] = 0
                userData[userID]["total_balance"] = 0
                userData[userID]["pick"] = "Copper Pick"

                with open(self.save_file, "w") as f:
                    json.dump(self.data, f)

                conv.send_message(toSeg("Successfully prestiged"))

        except:
            conv.send_message(toSeg("Something went wrong!"))

    def prestige_upgrade_info(self, bot, event):
        user, conv = getUserConv(bot, event)
        userData = self.data["users"]
        userID = user.id_[0]

        if userID not in userData:
            conv.send_message(toSeg("You are not registered! Use /register"))
            return

        prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** userData[userID]["prestige_upgrade"])
        conv.send_message(toSeg("By prestiging, you will lose " + str(prestige_upgrade_cost) + " prestige."))

    def prestige_upgrade(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        userData = self.data["users"]

        try:
            if userID not in userData:
                conv.send_message(toSeg("You are not registered! Use /register"))
                return

            else:
                prestige_upgrade_cost = math.floor(self.prestige_upgrade_base * 2.5 ** userData[userID]["prestige_upgrade"])

                if userData[userID]["prestige"] < prestige_upgrade_cost:
                    conv.send_message(toSeg("That costs " + str(prestige_upgrade_cost) + " prestige, which you don't have enough of!"))
                    return

                else:
                    userData[userID]["prestige_upgrade"] += 1
                    userData[userID]["prestige"] -= prestige_upgrade_cost
                    self.data["users"][userID]["prestige_upgrade_confirm"] = 0

                    with open(self.save_file, "w") as f:
                        json.dump(self.data, f)

                conv.send_message(toSeg("Successfully upgraded prestige!"))

        except Exception as e:
            conv.send_message(toSeg("Something went wrong!"))
            print(e)
