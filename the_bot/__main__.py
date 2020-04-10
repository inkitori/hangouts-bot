"""
hangouts bot with games
"""
from bot import bots
import optparse


parser = optparse.OptionParser(description=__doc__)
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts", type="choice",
    choices=["hangouts", "console"],
    help="chooses a bot to run (hangouts(default) or console)",
)
id_option = optparse.make_option(
    "-i", "--id", dest="userid", default=101, type="int",
    help="the id to use",
)
parser.add_options([bot_option, id_option])


def choose_bot_arguments():
    (options, args) = parser.parse_args()
    optparse.check_choice(bot_option, "bot", options.bot)
    return bots[options.bot](userID=options.userid)


bot = choose_bot_arguments()
bot.run()
