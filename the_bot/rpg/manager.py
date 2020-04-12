"""
manager for rpg
"""
from datetime import datetime
import random
import utils
from rpg.player_class import RPG


class RPGManager:
    """manager for rpg"""

    save_file = "the_bot/rpg/save_data.json"
    game = RPG()

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

        self.load_game()

        random.seed(datetime.now())

    def register(self):
        """registers a user"""
        pass

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        used_command = True
        if not command:
            return "you must enter a command"

        if command != "register" and userID not in RPG.players:
            return "You are not registered! Use register"
        # more commands here?
        else:
            used_command = False
        command = "" if used_command else command
        return self.game.play_game(userID, commands, command=command)

    def load_game(self):
        """loads the game"""
        pass

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for userID, player in save_data.items():
            save_data[userID] = player.to_dict()

        utils.save(self.save_file, save_data)
