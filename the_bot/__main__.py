"""
runs the bot
"""
import bot
import config


def stuff(handler):
    """
    for running random stuff
    mainly used for changing data
    """
    pass


options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
stuff(handler=current_bot.handler)
current_bot.run()
