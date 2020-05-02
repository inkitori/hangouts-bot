"""
sets up parser for arguments
"""
import argparse

parser = argparse.ArgumentParser(description="a bot for hangouts")

# bot selection
bots_args = parser.add_argument_group("Bots")
bots_args.add_argument(
    "-o", "--hangouts",
    action="store_const", const="hangouts", dest="bot", default="hangouts",
    help="runs the hangouts bot",
)
bots_args.add_argument(
    "-c", "--console",
    action="store_const", const="console", dest="bot", default="hangouts",
    help="runs the console bot",
)
bots_args.add_argument(
    "-t", "--test",
    action="store_const", const="test", dest="bot", default="hangouts",
    help="tests bot in console",
)

user_args = parser.add_argument_group("User")
user_args.add_argument(
    "-i", "--id", dest="user_id", default=101, type=int,
    help="user id for games",
)
user_args.add_argument(
    "-k", "--token", dest="token", default="token.txt",
    help="hangouts login token",
)

# data loaing/deleting
data_args = parser.add_argument_group("Data")
data_args.add_argument(
    "-s", "--skip-sheets", dest="load_sheets", action="store_false", default=True,
    help="skips loading sheets",
)
data_args.add_argument(
    "-w", "--wipe-data", dest="wipe", default=None,
    choices=["rpg", "economy", "2048"],
    help="wipes a game's data from save_data",
)
data_args.add_argument(
    "-f", "--save-file", dest="save_file", default="save_data",
    help="sets the file to save and load from",
)


def parse_arguments():
    """parses the arguments"""
    return parser.parse_args()
