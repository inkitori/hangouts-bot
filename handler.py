import hangups
import asyncio
# import random
# from text_2048 import play_game
from collections import defaultdict


class Handler:
    def __init__(self):
        self.keywords = {
            "good bot": "nyaa, thanku~~",
            "bad bot": "nuu dun pweese~~ >.<",
            "headpat": "uwu thanku",
            "yamete": "kudasai!~~",
            "ping": "pong"
        }
        self.commands = {
            "/help": self.help,
            "/rename": self.rename,
            "/say": self.say,
            "/rickroll": self.rickroll,
            "/quit": self.quit
        }
        self.images = {
            "/gay": "images/gay.jpg",
            "/math": "images/math.jpg",
            "/praise": "images/praise.jpg",
            "/goddammit": "images/goddammit.jpg",
            # "/heymister": "images/heymister.png"
        }
        self.users = defaultdict(dict)
        self.admins = [
            "yelloweywatermelons@gmail.com",
            "mskikotang@gmail.com",
            "chendi.luo@gmail.com",
            "creonalia@gmail.com",
            "galaxiesgirls2000@gmail.com"
        ]

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 3):
            return

        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 3):
            return

        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str(event.text.split(' ', 1)[1]))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /say {message}"))

    async def rickroll(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 2):
            return

        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Something went wrong!"))

    async def quit(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            if str(user.emails).strip().lower()[2:-2] in self.admins:
                await conv.send_message(hangups.ChatMessageSegment.from_str("Saber out!"))
                await bot.client.disconnect()
            else:
                await conv.send_message(hangups.ChatMessageSegment.from_str("bro wtf u can't use that"))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Something went wrong!"))

    async def help(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 10):
            return

        f = open("help.txt", 'r')
        contents = f.read()
        await conv.send_message(hangups.ChatMessageSegment.from_str(contents))
        f.close()

    def cooldown(self, user, event, cooldown):
        text = event.text.lower()

        if user in self.users and text.split()[0] in self.users[user]:
            if (event.timestamp - self.users[user][text.split()[0]]).seconds < cooldown:
                print(cooldown - (event.timestamp - self.users[user][text.split()[0]]).seconds)
                return 1
            else:
                self.users[user][text.split()[0]] = event.timestamp
                return 0
        else:
            self.users[user][text.split()[0]] = event.timestamp
            print("bruh")
            return 0


def getUserConv(bot, event):
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)

    return user, conv
