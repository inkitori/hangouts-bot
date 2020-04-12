"""
manager for rpg
"""
from datetime import datetime
import random
import utils
import rpg.player_class as classes


class RPGManager:
    """manager for rpg"""

    save_file = "the_bot/rpg/save_data.json"
    game = classes.RPG()

    def __init__(self):
        self.load_game()

        random.seed(datetime.now())

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        used_command = True
        if not command:
            return "you must enter a command"

        if command != "register" and userID not in self.game.players:
            return "You are not registered! Use register"
        else:
            used_command = False
        command = "" if used_command else command
        return self.game.play_game(userID, commands, command=command)

    def load_game(self):
        """loads the game"""
        save_data = utils.load(self.save_file)
        for userID, player_data in save_data.items():
            self.game.players[int(userID)] = classes.Player(**player_data)

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for userID, player in save_data.items():
            save_data[userID] = player._to_dict()

        utils.save(self.save_file, save_data)
