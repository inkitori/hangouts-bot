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
    sheet_ID = "1H9m57A7vcSvGnEIrAKAHjg-GmvKw1GqQqQdAMeuN5do"

    def __init__(self):
        self.load_game()
        random.seed(datetime.now())

    def run_game(self, user_ID, commands):
        """runs the game"""
        command = next(commands)
        if not command:
            return "you must enter a command"

        if command != "register" and user_ID not in self.game.players:
            return "You are not registered! Use register"
        else:
            commands.send(-1)
        return self.game.play_game(user_ID, commands)

    def load_game(self):
        """loads the game"""
        save_data = utils.load(self.save_file)
        for user_ID, player_data in save_data.items():
            self.game.players[int(user_ID)] = player_class.Player(**player_data)
        self.load_sheets_data()

    def load_sheets_data(self):
        sheets = self.sheets_service.spreadsheets()
        named_ranges = utils.get_named_ranges(
            sheets, spreadsheetID=self.sheet_ID,
            sheet_name="RPG",
            )

        spreadsheet_data = sheets.values().get(
            spreadsheetId=self.sheet_ID,
            range=named_ranges["items"]
        ).execute()
        values = spreadsheet_data.get("values", [])
        print(utils.join_items(
            *[row for row in values if row],
            is_description=True,
        ))

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for user_ID, player in save_data.items():
            save_data[user_ID] = player.to_dict()

        utils.save(self.save_file, save_data)
