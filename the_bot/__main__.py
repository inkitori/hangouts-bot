"""
runs the bot
"""
from bot import bots
import utils
import sys
import optparse
# TODO: use opt parse instead of input


def choose_bot_input():
    """
    lets the user manually choose a bot
    replaced by command line arguments
    """
    bot_selection_text = "Pick a bot from the list below or use quit\n"
    bot_selection_text += utils.newline(utils.join_items(
        *[(name, bot.__doc__) for name, bot in bots.items()], is_description=True
    ))
    command = ""
    while command not in bots.keys():
        commands = utils.command_parser(input(bot_selection_text))
        command = next(commands)
        if command == "quit":
            sys.exit()

    return bots[command]()


bot = choose_bot_input()
bot.run()
