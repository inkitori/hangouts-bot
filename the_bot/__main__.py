"""
runs the bot
"""
import bot
import config


def stuff(handler):
    """for running random stuff"""
    for player_id in (101, 102, 103):
        try:
            del handler.game_managers["/rpg"].game.players[player_id]
        except KeyError:
            continue


options = config.parse_arguments()
current_bot = bot.bots[options.bot](options)
stuff(handler=current_bot.handler)
current_bot.run()
