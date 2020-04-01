import hangups
from hangups import hangouts_pb2
from hangups.hangouts_pb2 import ParticipantId

import asyncio
from text_2048 import run_game
import random
from collections import defaultdict
from datetime import datetime, tzinfo
import json
import math

from utils import *


class Handler:
    def __init__(self):
        self.keywords = {
            "good bot": "nyaa, thanku~~",
            "bad bot": "nuu dun pweese~~ >.<",
            "headpat": "uwu thanku",
            "yamete": "kudasai!~~",
            "ping": "pong",
            "pong": "ping",
            "saber": "hi",
            "yes": "no",
            "no": "yes"
        }
        self.commands = {
            "/help": self.help,
            "/rename": self.rename,
            "/say": self.say,
            "/rickroll": self.rickroll,
            "/quit": self.quit,
            "/reset": self.reset,
            "/id": self.id,
            "/kick": self.kick,
            "/register": self.register,
            "/balance": self.balance,
            "/mine": self.mine,
            "/save": self.save,
            "/shop": self.shop,
            "/buy": self.buy,
            "/give": self.give,
            "/id_give": self.id_give,
            "/profile": self.profile,
            "/leaderboard": self.leaderboard,
            "/prestige": self.prestige,
            "/prestige_confirm": self.prestige_confirm,
            "/sync": self.sync,
            "/2048": self.play_2048
        }
        self.images = {
            "/gay": "images/gay.jpg",
            "/math": "images/math.jpg",
            "/praise": "images/praise.jpg",
            "/goddammit": "images/goddammit.jpg",
            "/heymister": "images/heymister.png"
        }

        self.cooldowns = defaultdict(dict)
        self.admins = [
            114207595761187114730,  # joseph
            106637925595968853122,  # chendi
            ]
        self.ignore = [105849946242372037157]
        self.prestige_conversion = 100000
        random.seed(datetime.now())

        with open("data.json") as f:
            self.data = json.load(f)

    # utility
    async def help(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        f = open("text/help.txt", 'r')
        contents = f.read()
        await conv.send_message(toSeg(contents))
        f.close()

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except:
            await conv.send_message(toSeg("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.send_message(toSeg(event.text.split(' ', 1)[1]))
        except:
            await conv.send_message(toSeg("Format: /say {message}"))

    async def id(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            await conv.send_message(toSeg(user.id_[0]))
        except:
            await conv.send_message(toSeg(str("Something went wrong!")))

    async def kick(self, bot, event):
        user, conv = getUserConv(bot, event)
        arg1 = event.text.lower().split()[1]
        users = conv.users
        ids = []
        kick_users = []

        try:
            for user in users:
                if arg1 in user.full_name.lower():
                    kick_users.append(user)

            if not kick_users:
                await conv.send_message(toSeg("Nobody in this conversation goes by that name"))
                return
            # only reason i figured this out was because of hangupsbot, so thank you so much https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

            ids = [ParticipantId(gaia_id=user.id_.gaia_id, chat_id=conv.id_) for user in kick_users]

            for kick_id in ids:
                request = hangouts_pb2.RemoveUserRequest(
                    request_header=bot.client.get_request_header(),
                    participant_id=kick_id,
                    event_request_header=conv._get_event_request_header()
                )
                res = await bot.client.remove_user(request)
                conv.add_event(res.created_event)
        except:
            await conv.send_message(toSeg("Yeah don't use this command lol"))

    # fun
    async def rickroll(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.send_message(toSeg("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

    async def play_2048(self, bot, event):
        game_text = run_game(event.text)
        await conv.send_message(toSeg(game_text))

    # economy
    async def register(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        if userID in self.data["users"]:
            await conv.send_message(toSeg("You are already registered!"))
            return

        try:
            self.data["users"][userID] = user
            self.data["users"][userID] = {}
            self.data["users"][userID]["balance"] = 0
            self.data["users"][userID]["total_balance"] = 0
            self.data["users"][userID]["prestige"] = 0
            self.data["users"][userID]["pick"] = "Copper Pick"
            self.data["users"][userID]["name"] = user.full_name

            with open("data.json", "w") as f:
                json.dump(self.data, f)

            await conv.send_message(toSeg("Successfully registered!"))
        except Exception as e:
            await conv.send_message(toSeg("Failed to register!"))
            print(e)

    async def balance(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        if userID not in self.data["users"]:
            await conv.send_message(toSeg("You are not registered! Use /register"))
            return

        try:
            balance = self.data["users"][userID]["balance"]
            await conv.send_message(toSeg(user.full_name + ", you currently have " + str(balance) + " Saber Dollars!"))
        except Exception as e:
            await conv.send_message(toSeg("Failed to retrieve balance info!"))
            print(e)

    async def mine(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if userID not in self.data["users"]:
            await conv.send_message(toSeg("You are not registered! Use /register"))
            return

        i = cooldown(self.cooldowns, user, event, 4)
        if i:
            await conv.send_message(toSeg("On cooldown. Please wait " + str(i) + " second(s)."))
            return

        try:
            playerPick = self.data["shop"]["pick"][self.data["users"][userID]["pick"]]
            mined_amt = random.randint(playerPick["range"][0], playerPick["range"][1])
            mined_amt += math.ceil(mined_amt * self.data["users"][userID]["prestige"] / 100)

            self.data["users"][userID]["balance"] += mined_amt
            self.data["users"][userID]["total_balance"] += mined_amt

            with open("data.json", "w") as f:
                json.dump(self.data, f)

            await conv.send_message(toSeg(user.full_name + ", you mined " + str(mined_amt) + " Saber Dollars!"))

        except Exception as e:
            await conv.send_message(toSeg("Failed to mine!"))
            print(e)

    async def shop(self, bot, event):
        user, conv = getUserConv(bot, event)

        if cooldown(self.cooldowns, user, event, 20):
            return

        try:
            with open("text/shop.txt", "r") as f:
                s = f.read()
                await conv.send_message(toSeg(s))
        except:
            await conv.send_message(toSeg("Failed to retrieve shop!"))

    async def buy(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            item_type = event.text.split()[1].lower()
            item = event.text.split(' ', 2)[2].strip().lower().title()

            if userID not in self.data["users"]:
                await conv.send_message(toSeg("You are not registered!  Use /register"))
                return

            elif item == "Top":
                if item_type not in self.data["shop"]:
                    await conv.send_message(toSeg("That class doesn't exist!"))
                    return

                else:
                    shopData = self.data["shop"][item_type]
                    userData = self.data["users"][userID]
                    possible_items = []

                    for possible_item in shopData:
                        if shopData[possible_item]["value"] > shopData[userData["pick"]]["value"] and shopData[possible_item]["price"] <= userData["balance"]:
                            possible_items.append(possible_item)

                    if len(possible_items) == 0:
                        await conv.send_message(toSeg("No possible item of that class you can purchase!"))
                        print("test")
                        return

                    else:
                        purchase = possible_items[-1]
                        userData[item_type] = shopData[purchase]["name"]
                        userData["balance"] -= shopData[purchase]["price"]

                        with open("data.json", "w") as f:
                            json.dump(self.data, f)

                        await conv.send_message(toSeg("Successful purchase of the " + purchase + "!"))
                        return

            elif item_type not in self.data["shop"] or item not in self.data["shop"][item_type]:
                await conv.send_message(toSeg("That item doesn't exist!"))
                return
            else:
                if self.data["users"][userID]["balance"] < self.data["shop"][item_type][item]["price"]:
                    await conv.send_message(toSeg("You don't have enough money for that!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] == self.data["shop"][item_type][item]["value"]:
                    await conv.send_message(toSeg("You already have that pick!"))
                    return
                elif self.data["shop"][item_type][self.data["users"][userID][item_type]]["value"] > self.data["shop"][item_type][item]["value"]:
                    await conv.send_message(toSeg("You already have a pick better than that!"))
                    return
                else:
                    self.data["users"][userID][item_type] = self.data["shop"][item_type][item]["name"]
                    self.data["users"][userID]["balance"] -= self.data["shop"][item_type][item]["price"]

                    with open("data.json", "w") as f:
                        json.dump(self.data, f)

                    await conv.send_message(toSeg("Purchase successful!"))
        except Exception as e:
            await conv.send_message(toSeg("Format: /buy {type} {item}"))
            print(e)

    async def give(self, bot, event):
        user, conv = getUserConv(bot, event)
        users = conv.users
        userID = user.id_[0]
        give_users = []

        try:
            arg1 = event.text.split(' ', 1)[1]
            arg1 = arg1.rsplit(' ', 1)[0]

            arg2 = int(event.text.split()[-1])

            if isIn(self.ignore, user):
                await conv.send_message(toSeg("You are an ignored user!"))
                return

            for u in users:
                if arg1 in u.full_name:
                    give_users.append(u)

            if userID not in self.data["users"]:
                await conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif len(give_users) != 1:
                await conv.send_message(toSeg("Error finding that user! Try /id_give instead."))
                return

            elif give_users[0].id_[0] not in self.data["users"]:
                await conv.send_message(toSeg("That user has not registered!"))
                return

            elif give_users[0].id_[0] == user.id_[0]:
                await conv.send_message(toSeg("That user is you!"))
                return

            elif arg2 < 0:
                await conv.send_message(toSeg("You can't give negative money!"))
                return

            elif self.data["users"][userID]["balance"] < arg2:
                await conv.send_message(toSeg("You don't have enough money to do that!"))
                return

            else:
                self.data["users"][userID]["balance"] -= arg2
                self.data["users"][give_users[0].id_[0]]["balance"] += arg2
                self.data["users"][give_users[0].id_[0]]["total_balance"] += arg2

                with open("data.json", "w") as f:
                    json.dump(self.data, f)

                await conv.send_message(toSeg("Successfully given " + str(arg2) + " Saber Dollars to " + give_users[0].full_name))
                await conv.send_message(toSeg("That user now has " + str(self.data["users"][give_users[0].id_[0]]["balance"]) + " Saber Dollars"))

        except:
            await conv.send_message(toSeg("Format: /give {user} {money}"))

    async def id_give(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        try:
            give_user = event.text.split()[1]
            give_money = int(event.text.split()[-1])

            if isIn(self.ignore, user):
                await conv.send_message(toSeg("You are an ignored user!"))
                return

            if userID not in self.data["users"]:
                await conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif give_user not in self.data["users"]:
                await conv.send_message(toSeg("That user has not registered!"))
                return

            elif userID == give_user:
                await conv.send_message(toSeg("That user is you!"))
                return

            elif self.data["users"][userID]["balance"] < give_money:
                await conv.send_message(toSeg("You don't have enough money to do that!"))
                return

            elif give_money < 0:
                await conv.send_message(toSeg("You can't give negative money!"))
                return

            else:
                self.data["users"][userID]["balance"] -= give_money
                self.data["users"][give_user]["balance"] += give_money
                self.data["users"][give_user]["total_balance"] += give_money
                with open("data.json", "w") as f:
                    json.dump(self.data, f)
                await conv.send_message(toSeg("Successfully given " + str(give_money) + " Saber Dollars to ID: " + str(give_user)))
                await conv.send_message(toSeg("That user now has " + str(self.data["users"][give_user]["balance"]) + " Saber Dollars"))
        except:
            await conv.send_message(toSeg("Format: /id_give {id} {money}"))

    async def profile(self, bot, event):
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
                    await conv.send_message(toSeg("No users go by that name!"))
                    return

                elif len(possible_users) > 1:
                    await conv.send_message(toSeg(str(len(possible_users)) + " possible user(s) go by that name:\n"))

                    for user in possible_users:
                        await conv.send_message(toSeg(
                            "**Name:** " + dataUsers[user]["name"] + '\n' +  # multiple users
                            "**Balance:** " + str(dataUsers[user]["balance"]) + '\n' +
                            "**Pick:** " + dataUsers[user]["pick"] + '\n' +
                            "**Prestige:** " + str(dataUsers[user]["prestige"]) + '\n' +
                            "**ID:** " + user + '\n\n')
                        )
                else:
                    await conv.send_message(toSeg(
                        "**Name:** " + dataUsers[possible_users[0]]["name"] + '\n' +  # single user
                        "**Balance:** " + str(dataUsers[possible_users[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[possible_users[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[possible_users[0]]["prestige"]) + '\n' +
                        "**ID:** " + possible_users[0])
                    )

            else:
                if user.id_[0] in self.data["users"]:
                    await conv.send_message(toSeg(
                        "**Name:** " + self.data["users"][user.id_[0]]["name"] + '\n' +  # no args
                        "**Balance:** " + str(self.data["users"][user.id_[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[user.id_[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[user.id_[0]]["prestige"]) + '\n' +
                        "**ID:** " + user.id_[0])
                    )
        except Exception as e:
            await conv.send_message(toSeg("Failed to retrieve user info!"))
            print(e)

    async def leaderboard(self, bot, event):
        user, conv = getUserConv(bot, event)
        users = {}
        cnt = 1
        leaderboard = "Ranking by balanced earned in this lifetime:\n"

        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            for user in self.data["users"]:
                users[user] = (self.data["users"][user]["total_balance"])

            sorted_users = {key: value for key, value in sorted(users.items(), key=lambda x: x[1], reverse=True)}

            for key, value in sorted_users.items():
                if cnt == 6:
                    break

                leaderboard += str(cnt) + '. ' + self.data["users"][key]["name"] + ": " + str(value) + '\n'
                cnt += 1
            await conv.send_message(toSeg(leaderboard))

        except:
            await conv.send_message(toSeg("Failed retrieving leaderboard info!"))

    async def prestige(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        try:
            if userID not in self.data["users"]:
                await conv.send_message(toSeg("You are not registered! Use /register"))
                return

            current_prestige = self.data["users"][userID]["prestige"]
            earned_prestige = math.trunc(self.data["users"][userID]["total_balance"] / self.prestige_conversion)

            await conv.send_message(toSeg(
                "You currently have " + str(current_prestige) + " prestige point(s). If you prestige, you will earn " +
                str(earned_prestige) + " more prestige point(s), or a " +
                str(earned_prestige) + "% bonus, but will lose all your money and items.")
                )
            await conv.send_message(toSeg('Type "/prestige_confirm" if you really do wish to prestige.'))

            self.data["users"][userID]["prestige_confirm"] = 1

        except:
            await conv.send_message(toSeg("Something went wrong!"))

    async def prestige_confirm(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        userData = self.data["users"]

        try:
            if userID not in userData:
                await conv.send_message(toSeg("You are not registered! Use /register"))
                return

            elif not userData[userID]["prestige_confirm"]:
                await conv.send_message(toSeg('You have to use "/prestige" before using this command!'))
                return

            else:
                await conv.send_message(toSeg("Prestiging"))
                userData[userID]["balance"] = 0
                userData[userID]["prestige"] += math.trunc(userData[userID]["total_balance"] / self.prestige_conversion)
                userData[userID]["prestige_confirm"] = 0
                userData[userID]["total_balance"] = 0
                userData[userID]["pick"] = "Copper Pick"

                with open("data.json", "w") as f:
                    json.dump(self.data, f)

                await conv.send_message(toSeg("Successfully prestiged"))

        except:
            await conv.send_message(toSeg("Something went wrong!"))

    # config
    async def quit(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 30):
            return

        try:
            if isIn(self.admins, user):
                await conv.send_message(toSeg("Saber out!"))
                await bot.client.disconnect()
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

    async def reset(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            arg1 = '/' + event.text.lower().split()[1]
            if isIn(self.admins, user):
                if arg1 in self.cooldowns[user]:
                    self.cooldowns[user][arg1] = datetime.min.replace(tzinfo=None)
                else:
                    await conv.send_message(toSeg("Format: /reset {command}"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Format: /reset {command}"))

    async def save(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            if isIn(self.admins, user):
                with open("data.json", "w") as f:
                    json.dump(self.data, f)
                await conv.send_message(toSeg("Successfully saved!"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

    async def sync(self, bot, event):
        user, conv = getUserConv(bot, event)
        key = event.text.lower().split()[1]
        value = event.text.lower().split(' ', 2)[2]

        if value.isdigit():
            value = int(value)

        try:
            if isIn(self.admins, user):
                for user in self.data["users"]:
                    self.data["users"][user][key] = value

                    with open("data.json", "w") as f:
                        json.dump(self.data, f)

                    await conv.send_message(toSeg("Synced all values!"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))

        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            print(e)
