"""
runs the bot
"""
import bot
import config
import utils


def wipe_data(game):
    """wipes data from save_data"""
    # TODO: make data_keys frpm managers, insteadof cpoying names
    # TODO: get data_keys.keys() in config -wipe-data for choices instead of copying literals
    # TODO: option to wipe all data
    # TODO: option to wipe some data (wipe 2048 games, but not 2048 high scores)
    # TODO: get default values from managers insteadd og  hardcoding here
    # TODO: option to wipe and log some data (only inventories)
    if not game:
        return
    data_keys = {
        "economy": {"economy_players": {}},
        "2048": {"games_2048": {"current game": None}, "scores_2048": {}},
        "rpg": {"rpg_players": {}}
    }
    utils.save(**data_keys[game])


args = config.parse_arguments()
wipe_data(args.wipe)
current_bot = bot.bots[args.bot](args)
current_bot.run()
