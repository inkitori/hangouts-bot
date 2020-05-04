"""
runs the bot
"""
import config
import utils

args = config.parse_arguments()
if args.wipe:
    utils.wipe_data(args.wipe)
utils.save_file_name = args.save_file
import bot  # prevents errors with wiping/loading data since the import loads the data
current_bot = bot.bots[args.bot](args)
current_bot.run()
