import hangups
from hangups import hangouts_pb2
from hangups.hangouts_pb2 import ParticipantId
import asyncio
import random
from collections import defaultdict
from datetime import datetime, tzinfo
import json
import math
from utils import *

from game_2048.manager_2048 import Manager as Manager2048
import economy
from rpghandler import RPGHandler


class Handler:

    save_file = "the_bot/data.json"
    images_folder = "the_bot/images/"

    keywords = {
        "ping": "pong",
        "pong": "ping",
        "saber": "hi",
        "meep": "meep"
    }
    images = {
        "/gay": "gay.jpg",
        "/math": "math.jpg",
        "/praise": "praise.jpg",
        "/goddammit": "goddammit.jpg",
        "/heymister": "heymister.png"
    }

    def __init__(self):
        self.manager_2048 = Manager2048()
        self.rpg_handler = RPGHandler()
        self.commands = {
            "/help": self.help_,
            "/rename": self.rename,
            "/quit": self.quit_,
            "/id": self.id_,
            "/kick": self.kick,
            "/economy": self.economy,
            "/2048": self.play_2048,
            "/rpg": self.rpg,
            "say_something": self.say_something,
        }
        self.cooldowns = defaultdict(dict)
        self.admins = [
            114207595761187114730,  # joseph
            106637925595968853122,  # chendi
        ]
        self.ignore = [
            105849946242372037157,  # odlebot
            11470746254329358783,  # saberbot
            104687919952293193271,  # Ether(chendibot)
        ]

        random.seed(datetime.now())

        with open(self.save_file) as f:
            self.data = json.load(f)

    # utility
    async def help_(self, bot, event):
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

    async def id_(self, bot, event):
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
            # only reason i figured this out was because of hangupsbot, so thank you so much
            # https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

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

    # games
    async def rpg(self, bot, event):
        user, conv = getUserConv(bot, event)
        rpg_text = self.rpg_handler.rpg_process(user.id_[0], event.text)
        print(rpg_text)

        await conv.send_message(toSeg(rpg_text))

    async def play_2048(self, bot, event):
        user, conv = getUserConv(bot, event)
        game_text = self.manager_2048.run_game(event.text)
        await conv.send_message(toSeg(game_text))
        self.manager.save_games()

    async def economy(self, bot, event):
        pass

    async def quit_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 30):
            return

        if userIn(self.admins, user):
            await conv.send_message(toSeg("Saber out!"))
            save_games()
            await bot.client.disconnect()
        else:
            await conv.send_message(toSeg("bro wtf u can't use that"))
