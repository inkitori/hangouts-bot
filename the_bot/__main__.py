"""
hangouts bot with games
"""
from bot import bots
import utils
import sys
import optparse


parser = optparse.OptionParser(description=__doc__)
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts",
    choices=["hangouts", "console"],
    help="chooses a bot to run (hangouts(default) or console)",
)
parser.add_option(bot_option)


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


def choose_bot_arguments():
    (options, args) = parser.parse_args()
    optparse.check_choice(bot_option, "bot", options.bot)
    return bots[options.bot]()


bot = choose_bot_arguments()
bot.run()
