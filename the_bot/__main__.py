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
    return
    game_managers = handler.game_managers
    manager = game_managers["/rpg"]
    rpg = manager.game
    rpg.players = {}
    manager.save_game()
    import sys
    sys.exit()


args = config.parse_arguments()
current_bot = bot.bots[args.bot](args)
stuff(handler=current_bot.handler)
current_bot.run()
