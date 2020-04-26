"""
runs the bot
"""
import config
import bot


options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
current_bot.run()
