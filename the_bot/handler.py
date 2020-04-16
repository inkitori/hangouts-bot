"""
handler for bots
"""
from hangups import hangouts_pb2 as hangouts_pb2

import random
from collections import defaultdict
from datetime import datetime
import utils

from game_2048.manager import Manager2048
from economy.manager import EconomyManager
from rpg.manager import RPGManager


class Handler:
    """handler for bot"""
    game_managers = {
        "/2048": Manager2048(),
        "/rpg": RPGManager(),
        "/economy": EconomyManager(),
    }
    admins = (
        114207595761187114730,  # joseph
        117790385966808489693,  # joseph's new account
        106637925595968853122,  # chendi
        103828905050116935505,  # bill
    )

    def __init__(self):
        self.cooldowns = defaultdict(dict)
        random.seed(datetime.now())

    async def handle_message(self, event, console=False, userID=101, bot=None):
        """handles messages"""
        text = event if console else event.text
        if not console:
            user, conv = utils.get_user_and_conv(bot, event)
        commands = utils.command_parser(text)
        command = next(commands)

        # deals with commands
        if command in self.keywords:
            output_text = self.keywords[command]

        elif command in self.commands:
            if console:
                output_text = f"command {command} is not available outside of hangouts"
            else:
                output_text = await self.commands[command](self, bot, user, conv, commands)

        elif command in self.game_managers:
            userID = userID if console else user.id_[0]
            output_text = self.play_game(userID, command, commands)
            if console:
                # 2048 is designed to print for hangouts, where each numeral is the same width as 2 spaces
                # consoles are monospaced, so this fixes that
                output_text = output_text.replace("  ", " ")

        else:
            # if this printed in hangouts, it would respond to every single message
            output_text = "Invalid command" if console else ""

        return output_text

    async def rename_conv(self, bot, user, conv, commands):
        """renames a conversation"""
        new_name = commands.send("remaining")
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
            # not sure why this ould happen, but just in case
            output_text = "Could not get id"
        return output_text

    async def kick(self, bot, user, conv, commands):
        """
        kicks a user
        last i checked, this was broken
        """
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
            print("Saber out!")
            await bot.client.disconnect()
        else:
            return "bro wtf u can't use that"

    commands = {
        "/rename": rename_conv,
        "/quit": quit_,
        "/id": id_,
        "/kick": kick,
    }
    keywords = {
        "ping": "pong",
        "pong": "ping",
        "saber": "hi",
        "meep": "meep",
        "/help": ""  # this avoids errors where keywords and help_text reference eachother
    }
    help_text = utils.join_items(
        "I'm a bot by Yeah and Chendi.",
        "You can view my source at https://github.com/YellowPapaya/hangouts-bot or suggest at https://saberbot.page.link/R6GT",
    ) + utils.join_items(
        ("keywords", *list(keywords)),
        ("games", *list(game_managers)),
        ("commands", *list(commands)),
        is_description=True, description_mode="long"
    )
    keywords["/help"] = help_text
