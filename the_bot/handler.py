"""
handler for bots
"""
import hangups
from hangups import hangouts_pb2 as hangouts_pb2

import asyncio
import random
from collections import defaultdict
from datetime import datetime  # , tzinfo
import utils

from game_2048.manager import Manager2048
# from economy.manager import EconomyManager
# from rpg.manager import RPGManager


class Handler:
    """handler for bot"""
    game_managers = {
        "/2048": Manager2048(),
        # "/rpg": RPGManager(),
        # "/economy": EconomyManager(),
    }
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    def __init__(self):
        self.commands = {
            "/rename": self.rename_conv,
            "/quit": self.quit_,
            "/id": self.id_,
            "/kick": self.kick,
        }
        self.keywords = {
            "ping": "pong",
            "pong": "ping",
            "saber": "hi",
            "meep": "meep",
            "/help": "placeholder"  # this avoids errors where keywords and help_text reference eachother
        }
        self.help_text = utils.join_items(
            "I'm a bot by Yeah and Chendi.",
            "You can view my source at https://github.com/YellowPapaya/hangouts-bot or suggest at https://saberbot.page.link/R6GT",
            # TODO: make this a loop
            utils.description("keywords", *list(self.keywords), long=True),
            utils.description("games", *list(self.game_managers), long=True),
            utils.description("commands", *list(self.commands), long=True),
        )
        self.keywords["/help"] = self.help_text

        self.cooldowns = defaultdict(dict)
        random.seed(datetime.now())

    async def handle_message(self, event, console=False, userID=101, bot=None):
        """handles messages"""
        text = event if console else event.text
        if not console:
            user, conv = utils.getUserConv(bot, event)
        commands = utils.command_parser(text)
        command = next(commands)

        if command in self.keywords:
            output_text = self.keywords[command]

        elif command in self.commands:
            function_ = self.commands[command]

            if console:
                output_text = f"command {command} is not available outside of hangouts"
            else:
                # function_cooldown_time = 0  # TODO: get the default cooldown for the function
                # if utils.cooldown(self.cooldowns, user, event, function_cooldown_time):
                    # output_text = "You are on cooldown"
                # else:
                output_text = await function_(bot, user, conv, commands)

        elif command in self.game_managers:
            userID = userID if console else user.id_[0]
            output_text = self.play_game(userID, command, commands)

        else:
            output_text = "Invalid command" if console else ""

        return output_text

    async def rename_conv(self, bot, user, conv, commands):
        """renames a conversation"""
        new_name = next(commands)
        if not new_name:
            return "Format: /rename {name}"
        else:
            await conv.rename(new_name)
            return "Sucessfully renamed"

    async def id_(self, bot, user, conv):
        """get the id of a user"""
        try:
            output_text = user.id_[0]
        except Exception:
            output_text = "Could not get id"
        return output_text

    async def kick(self, bot, user, conv, commands):
        """kicks a user"""
        kick_user_name = next(commands)
        users = conv.users

        try:
            for user in users:
                if kick_user_name in user.full_name.lower():
                    kick_user = kick_user_name
                    break

            if not kick_user:
                return "Nobody in this conversation goes by that name"
            # only reason i figured this out was because of hangupsbot, so thank you so much
            # https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

            kick_id = hangouts_pb2.ParticipantId(gaia_id=kick_user.id_.gaia_id, chat_id=conv.id_)

            request = hangouts_pb2.RemoveUserRequest(
                request_header=bot.client.get_request_header(),
                participant_id=kick_id,
                event_request_header=conv._get_event_request_header()
            )
            res = await bot.client.remove_user(request)
            conv.add_event(res.created_event)
        except Exception:
            output_text = "Yeah don't use this command lol"

        return output_text

    def play_game(self, userID, game_name, commands):
        """plays a game"""
        manager = self.game_managers[game_name]
        game_text = manager.run_game(userID, commands)
        manager.save_game()
        return game_text

    async def quit_(self, bot, user, conv, comands):
        """makes the bot quit"""
        if utils.userIn(self.admins, user):
            output_text = "Saber out!"
            await bot.client.disconnect()
        else:
            output_text = "bro wtf u can't use that"
        return output_text
