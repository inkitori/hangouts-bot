"""
hangouts bot with games
"""
from bot import bots
import optparse


parser = optparse.OptionParser(description=__doc__)
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts",
    choices=["hangouts", "console"],
    help="chooses a bot to run (hangouts(default) or console)",
)
parser.add_option(bot_option)


def choose_bot_arguments():
    (options, args) = parser.parse_args()
    optparse.check_choice(bot_option, "bot", options.bot)
    return bots[options.bot]()


bot = choose_bot_arguments()
bot.run()
