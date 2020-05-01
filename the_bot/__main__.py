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


args = config.parse_arguments()
current_bot = bot.bots[args.bot](args)
stuff(handler=current_bot.handler)
current_bot.run()
