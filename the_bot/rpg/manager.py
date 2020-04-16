"""
manager for rpg
"""
from datetime import datetime
import random
import utils
import rpg.rpg_class as rpg_class
import rpg.player_class as player_class


class RPGManager:
    """manager for rpg"""

    save_file = "the_bot/rpg/save_data.json"
    game = rpg_class.RPG()
    sheets_service = utils.create_sheets_service()

    def __init__(self):
        self.load_game()
        random.seed(datetime.now())

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        if not command:
            return "you must enter a command"

        if command != "register" and userID not in self.game.players:
            return "You are not registered! Use register"
        else:
            commands.send(-1)
        return self.game.play_game(userID, commands)

    def load_game(self):
        """loads the game"""
        save_data = utils.load(self.save_file)
        for userID, player_data in save_data.items():
            self.game.players[int(userID)] = player_class.Player(**player_data)
        sheets = self.sheets_service.spreadsheets()
        # load stuff from sheets here

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for userID, player in save_data.items():
            save_data[userID] = player.to_dict()

        utils.save(self.save_file, save_data)
