"""
handler for bot.Bot()
"""
import hangups
from hangups import hangouts_pb2
from hangouts_pb2 import ParticipantId
import asyncio
import random
from collections import defaultdict
from datetime import datetime  # , tzinfo
import utils

from game_2048.manager import Manager2048
from economy.manager import EconomyManager
from rpg.manager import RPGManager


class Handler:

    save_file = "data.json"
    images_folder = "images/"

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
    game_managers = {
        "/2048": Manager2048(),
        "/rpg": RPGManager(),
        "/economy": EconomyManager(),
    }
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    def __init__(self):
        self.commands = {
            "/help": self.help_,
            "/rename": self.rename_conv,
            "/quit": self.quit_,
            "/id": self.id_,
            "/kick": self.kick,
        }
        self.play_game.cooldown_time = 0
        self.help_.cooldown_time = 10
        self.rename_conv.cooldown_time = 3
        self.quit_.cooldown_time = 10
        self.id_.cooldown_time = 10
        self.kick.cooldown_time = 10

        self.cooldowns = defaultdict(dict)

        random.seed(datetime.now())

    # utility
    async def help_(self, bot, user, conv, commands):
        with open("text/help.txt", 'r') as help_text:
            bot.output_text = help_text.read()

    async def rename_conv(self, bot, user, conv, commands):
        new_name = next(commands)
        if not new_name:
            bot.output_text = "Format: /rename {name}"
        else:
            await conv.rename(new_name)

    async def id_(self, bot, user, conv):
        try:
            bot.output_text = user.id_[0]
        except Exception:
            bot.output_text = "Something went wrong!"

    async def kick(self, bot, user, conv, commands):
        kick_user_name = next(commands)
        users = conv.users

        try:
            for user in users:
                if kick_user_name in user.full_name.lower():
                    kick_user = kick_user_name
                    break

            if not kick_user:
                bot.output_text = "Nobody in this conversation goes by that name"
                return
            # only reason i figured this out was because of hangupsbot, so thank you so much
            # https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

            kick_id = ParticipantId(gaia_id=kick_user.id_.gaia_id, chat_id=conv.id_)

            request = hangouts_pb2.RemoveUserRequest(
                request_header=bot.client.get_request_header(),
                participant_id=kick_id,
                event_request_header=conv._get_event_request_header()
            )
            res = await bot.client.remove_user(request)
            conv.add_event(res.created_event)
        except Exception:
            bot.output_text = "Yeah don't use this command lol"

    async def play_game(self, bot, user, conv, commands):
        game_name = next(commands)
        manager = self.game_managers[game_name]
        game_text = manager.run_game(user.id_[0], commands)
        bot.output_text = game_text
        manager.save_game()

    async def quit_(self, bot, user, conv, comands):
        if utils.userIn(self.admins, user):
            bot.output_text = "Saber out!"
            await bot.client.disconnect()
        else:
            bot.output_text = "bro wtf u can't use that"
