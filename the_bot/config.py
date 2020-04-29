"""
sets up parser for arguments
"""
import optparse
import utils

console_bot = "--bot=console"
configurations = {
    # configuration_name: configuration_arguments in a list
    # feel free to add anything u want here, its fine
    "": [],  # prevents errors when no config is selected
    "con": [console_bot, ],
    "alt": [console_bot, "--id=102"],
    "adm": [console_bot, "--id=103"],
    "test": ["--bot=test", "--id=102"],
    "nwf": ["--bot=console", "--skip-sheets"],

}

# creating options
options = [
    optparse.make_option(
    "-b", "--bot", dest="bot", default="hangouts", type="choice",
        choices=["hangouts", "console", "test"],
        help="chooses a bot to run",
    ),
    optparse.make_option(
        "-i", "--id", dest="user_id", default=101, type="int",
        help="the id to use when using the console(default 101)",
    ),
    optparse.make_option(
        "-t", "--token", dest="token", default="token.txt",
        help="the token to use to login to hangouts",
    ),
    optparse.make_option(
        "-s", "--skip-sheets", dest="load_sheets", action="store_false", default=True,
        help="skips loading sheets",
    ),
    optparse.make_option(
        "-c", "--configuration", dest="config", default="", type="choice",
        choices=list(configurations),
        help="the configuration to use(overrides all other options)",
    ),
]

# creating and setting up parser
parser = optparse.OptionParser(description=__doc__)
parser.add_options(options)


def parse_arguments(configuration=""):
    """parses the arguments"""
    options, args = parser.parse_args()
    options.config = utils.default(configuration, options.config)

    if options.config:
        new_args = configurations[options.config]
        options, args = parser.parse_args(args=new_args)

    return options
