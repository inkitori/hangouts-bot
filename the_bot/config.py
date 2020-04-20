"""
sets up parser for arguments
"""
import optparse
import sys

configurations = {
    # configuration_name: configuration_arguments in a list
    # feel free to add anything u want here, its fine
    "": "",  # prevents errors when no config is selected
    "con": ["--bot=console", ],
    "alt": ["--bot=console", "--id=102"],
    "test": ["--bot=test", "--id=102"],
}

# creating options
bot_option = optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts", type="choice",
    choices=["hangouts", "console", "test"],
    help="chooses a bot to run",
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
    "-c", "--configuration", dest="config", default="", type="choice",
    choices=list(configurations),
    help="the configuration to use(overrides all other options)",
)

# creating and setting up parser
parser = optparse.OptionParser(description=__doc__)
parser.add_options([bot_option, id_option, token_option, config_option])




def parse_arguments(configuration=""):
    """parses the arguments"""
    options, args = parser.parse_args()
    options.config = configuration if configuration else options.config

    if options.config:
        new_args = configurations[options.config]
        options, args = parser.parse_args(args=new_args)

    return options
