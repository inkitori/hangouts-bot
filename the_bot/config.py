"""
sets up parser for arguments
"""
import argparse

parser = argparse.ArgumentParser(description="a bot for hangouts")

# bot selection
bots_args = parser.add_argument_group("bots")
bots_args.add_argument(
    "-b", "--bot", dest="bot", default="hangouts",
    choices=["hangouts", "console", "test"],
    help="chooses a bot to run",
)
bots_args.add_argument(
    "-o", "--hangouts",
    action="store_const", const="hangouts", dest="bot",
    help="runs the hangouts bot",
)
bots_args.add_argument(
    "-c", "--console",
    action="store_const", const="console", dest="bot",
    help="runs the console bot",
)
bots_args.add_argument(
    "-t", "--test",
    action="store_const", const="test", dest="bot",
    help="tests bot in console",
)

# configuring user
parser.add_argument(
    "-i", "--id", dest="user_id", default=101, type=int,
    help="the id to use when using the console (default 101)",
)
parser.add_argument(
    "-k", "--token", dest="token", default="token.txt",
    help="the token to use to login to hangouts",
)

# data loaing/deleting
parser.add_argument(
    "-s", "--skip-sheets", dest="load_sheets", action="store_false", default=True,
    help="skips loading sheets",
)
parser.add_argument(
    "-w", "--wipe-data", dest="wipe", default=None,
    choices=["rpg", "economy", "2048"],
    help="wipes a game's data from save_data",
)


def parse_arguments():
    """parses the arguments"""
    return parser.parse_args()
