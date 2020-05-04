"""
handler for bots
"""
import random
import collections
import datetime
import utils

from game_2048.manager import Manager2048
from economy.manager import EconomyManager
from rpg.manager import RPGManager


class Handler:
    """handler for bot"""
    admins = (
        114207595761187114730,  # joseph
        117790385966808489693,  # joseph's new account
        106637925595968853122,  # chendi
        103828905050116935505,  # bill
        103,  # for console testing
    )
    game_managers = {
        "2048": Manager2048(),
        "rpg": RPGManager(load_sheets=False),
        "eco": EconomyManager(),
    }
    image_folder = "the_bot/images/"
    images = {
        "llama": "llama.JPG",
        "ether": "ether.PNG",
        "penguin": "penguins1.GIF",
        "penguins": "penguins2.GIF",
        "more_penguins": "penguins3.GIF"
    }

    def __init__(self, *, console=False, load_sheets=True):
        self.cooldowns = collections.defaultdict(dict)
        self.console = console
        Handler.game_managers["/rpg"] = RPGManager(
            load_sheets=utils.default(load_sheets, not console, load_sheets is not None)
        )
        random.seed(datetime.datetime.now())

    async def handle_message(self, event, user_id=101, bot=None):
        """handles messages"""
        output_text = ""
        text = event if self.console else event.text
        if not self.console:
            user, conv = utils.get_user_and_conv(bot._convo_list, event)
        commands = utils.command_parser(text)
        command = next(commands)

        # deals with commands
        if command in self.keywords:
            output_text = self.keywords[command]

        elif command in self.images:
            if self.console:
                output_text = f"images are not available outside of hangouts, including {command}"
            else:
                with open(self.image_folder + self.images[command], "rb") as image:
                    await bot.send_image(image, conv)

        elif command in self.commands:
            if self.console:
                output_text = f"command {command} is not available outside of hangouts"
            else:
                output_text = await self.commands[command](self, bot, user, conv, commands)

        elif command in self.game_managers:
            user_id = user_id if self.console else user.id_[0]
            output_text = self.play_game(user_id, command, commands)
            # fixes difference in character width in hangouts vs monospaced consoles
            output_text = utils.default(output_text.replace("  ", " "), output_text, self.console)

        else:
            # if this printed in hangouts, it would respond to every single message
            output_text = utils.default("Invalid command", "", self.console)

        return output_text

    async def rename_conv(self, bot, user, conv, commands):
        """renames a conversation"""
        new_name = commands.send("remaining")
        if not new_name:
            return "Format: /rename {name}"
        else:
            return await bot.rename_conv(new_name)

    async def id_(self, bot, user, conv):
        """get the id of a user"""
        return user.id_[0]

    def play_game(self, user_id, game_name, commands):
        """plays a game"""
        manager = self.game_managers[game_name]
        game_text = manager.run_game(user_id, commands)
        manager.save_game()
        return game_text

    async def quit_(self, bot, user, conv, comands):
        """makes the bot quit"""
        if utils.user_in(self.admins, user):
            print("Saber out!")
            await bot.quit()
        else:
            return "bro wtf u can't use that"

    commands = {
        "/rename": rename_conv,
        "/quit": quit_,
        "/id": id_,
    }
    keywords = {
        "ping": "pong",
        "pong": "ping",
        "saber": "hi",
        "meep": "meep",
        "/help": ""  # this avoids errors where keywords and help_text reference eachother
    }
    help_text = utils.join_items(
        "I'm a bot by Astolfo and Chendi.",
        "You can view my source at https://github.com/YellowPapaya/hangouts-bot"
        " or suggest at https://saberbot.page.link/R6GT",
    ) + utils.join_items(
        ("keywords", *list(keywords)),
        ("games", *list(game_managers)),
        ("commands", *list(commands)),
        ("images", *list(images)),
        description_mode="long"
    )
    keywords["/help"] = help_text
