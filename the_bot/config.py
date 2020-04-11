"""
sets up parser for command lne arguments
"""
import optparse

parser = optparse.OptionParser(description=__doc__)
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts", type="choice",
    choices=["hangouts", "console"],
    help="chooses a bot to run (hangouts(default) or console)",
)
id_option = optparse.make_option(
    "-i", "--id", dest="userID", default=101, type="int",
    help="the id to use",
)
parser.add_options([bot_option, id_option])

def parse_arguments():
    (options, args) = parser.parse_args()
    optparse.check_choice(bot_option, "bot", options.bot)
    return options
