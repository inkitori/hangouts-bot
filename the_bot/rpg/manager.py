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
    game = rpg_class.RPG()
    spreadsheet_id = "1H9m57A7vcSvGnEIrAKAHjg-GmvKw1GqQqQdAMeuN5do"

    def __init__(self, load_sheets=True):
        self.load_game(load_sheets=load_sheets)
        random.seed(datetime.now())
        self.save_game()

    def run_game(self, player_id, commands):
        """runs the game"""
        player_id = int(player_id)
        command = next(commands)
        if not command:
            return "you must enter a command"

        if command != "register" and player_id not in self.game.players:
            return "You are not registered! Use register"
        else:
            commands.send(-1)
        return self.game.play_game(player_id, commands)

    def load_game(self, load_sheets):
        """loads the game"""
        self.game.players = utils.load("rpg_players")
        if load_sheets:
            print("loading rpg data from sheets")
            self.load_sheets_data()

    def load_sheets_data(self):
        sheets = utils.create_sheets_service().spreadsheets()
        named_ranges = utils.get_named_ranges(
            sheets, spreadsheet_id=self.spreadsheet_id,
            sheet_name="RPG",
        )

        item_data = sheets.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=named_ranges["items"]
        ).execute()
        item_data = item_data.get("values", [])

    def save_game(self):
        """saves the game"""
        utils.save(rpg_players=self.game.players)
        player_class.players = self.game.players
