"""
runs the bot
"""
import bot
import config

options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
current_bot.run()
debug 