"""
runs the bot
"""
import config
import bot

options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
try:
    current_bot.run()
except AttributeError:
    print("bot has no method run, add a run method")
