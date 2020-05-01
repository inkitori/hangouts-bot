"""
runs the bot
"""
import bot
import config


def stuff(handler=None):
    """
    for running random stuff
    mainly used for changing data
    """
    return
    import utils
    utils.save(rpg_players={})
    import sys
    sys.exit()


stuff()


args = config.parse_arguments()
current_bot = bot.bots[args.bot](args)
stuff(handler=current_bot.handler)
current_bot.run()
