"""
runs the bot
"""
import config
import bot

bots = {
    "hangouts": bot.Bot,
    "console": bot.ConsoleBot
}

options = config.parse_arguments()
current_bot = bots[options.bot](options)
current_bot.run()
