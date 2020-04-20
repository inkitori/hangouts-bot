"""
runs the bot
"""
import config
import bot
import test

test_options = config.parse_arguments("alt")
test.test(bot.bots["console"](test_options))

options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
current_bot.run()
