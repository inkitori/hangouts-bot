"""
runs the bot
"""
from bot import bots
import utils


# this should be changed to take an argument when running the code, but until then
bot_selection_text = utils.newline(utils.join_items(
    "Pick a bot from the list below or use quit",
    *[utils.description(name, bot.__doc__) for name, bot in bots.items()],
))
command = ""
while command not in bots.keys():
    commands = utils.command_parser(input(bot_selection_text))
    command = next(commands)
    print("your command is ", command)
    if command == "quit":
        break
else:
    bot = bots[command]()
    bot.run()
