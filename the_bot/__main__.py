"""
runs the bot
"""
import config
import bot
import test

test.test()

options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
current_bot.run()
