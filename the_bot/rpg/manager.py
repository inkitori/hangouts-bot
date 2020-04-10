"""
manager for rpg
"""
from datetime import datetime
import random
import utils
import rpg.classes as classes


class RPGManager:
    """manager for rpg"""

    save_file = "the_bot/rpg/save_data.json"
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )
    game = classes.RPG()

    def __init__(self):
        self.commands = {
            """
            "register": self.register,
            "inventory": self.inventory,
            "warp": self.warp,
            "equipped": self.equipped,
            "stats": self.stats,
            "rest": self.rest,
            "fight": self.fight,
            "atk": self.atk,
            "heal": self.heal
            """
        }
        self.admin_commands = {
            "remove": self.remove,
            "sync": self.sync,
            "save": self.save_game,
            "set": self.set_,
        }

        self.data = utils.load(self.save_file)
        self.userData = self.data["users"]

        random.seed(datetime.now())

    def register(self):
        """registers a user"""
        pass

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        if not command:
            return "you must enter a command"

        elif command not in list(self.commands) + list(self.admin_commands):
            return "That command doesn't exist!"

        elif command != "register" and userID not in classes.RPG.users:
            return "You are not registered! Use register"

        if command in self.admin_commands and not utils.userIn(self.admins, userID):
            return "bro wtf u cant use that"

        return self.commands[command](userID, commands)

    def load_game(self):
        """loads the game"""
        pass

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for userID, player in save_data:
            save_data[userID] = player.to_dict()

        utils.save(self.save_file, save_data)
