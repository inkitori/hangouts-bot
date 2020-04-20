"""
sets up parser for arguments
"""
import optparse
import sys

# creating options
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts", type="choice",
    choices=["hangouts", "console"],
    help="chooses a bot to run (hangouts(default) or console)",
)
id_option = optparse.make_option(
    "-i", "--id", dest="user_ID", default=101, type="int",
    help="the id to use when using the console(default 101)",
)
token_option = optparse.make_option(
    "-t", "--token", dest="token", default="token.txt",
    help="the token to use to login to hangouts",
)
config_option = optparse.make_option(
    "-c", "--configuration", dest="config", default="",
    help="the configuration to use(overrides all other options)",
)

# creating and setting up parser
parser = optparse.OptionParser(description=__doc__)
parser.add_options([bot_option, id_option, token_option, config_option])

configurations = {
    # configuration_name: configuration_arguments in a list
    # feel free to add anything u want here, its fine
    "con": ["--bot=console", ],
    "alt": ["--bot=console", "--id=102"]
}


def parse_arguments():
    """parses the arguments"""
    options, args = parser.parse_args()
    
    # checks and setups up configuration
    if options.config:
        try:
            new_args = configurations[options.config]
        except KeyError:
            print("that configuration does not exist")
            sys.exit()
        options, args = parser.parse_args(args=new_args)

    # checks the --bot argument
    optparse.check_choice(bot_option, "bot", options.bot)

    return options
