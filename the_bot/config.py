"""
sets up parser for arguments
"""
import optparse
import sys

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
token_option = optparse.make_option(
    "-t", "--token", dest="token", default="token.txt",
    help="the token to use",
)
config_option = optparse.make_option(
    "-c", "--configuration", dest="config", default="",
    help="the configuration to use(overrides all other options)",
)
parser.add_options([bot_option, id_option, token_option, config_option])

configurations = {
    # configuration_name: configuration_arguments in a list
    "con": ["--bot=console",]
}


def parse_arguments():
    """parses the arguments"""
    options, args = parser.parse_args()
    if options.config:
        try:
            new_args = configurations[options.config]
        except KeyError:
            print("that configuration does not exist")
            sys.exit()
        options, args = parser.parse_args(args=new_args)
    optparse.check_choice(bot_option, "bot", options.bot)
    return options
