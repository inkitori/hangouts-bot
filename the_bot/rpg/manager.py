"""
manager for rpg
"""
from datetime import datetime
import random
import utils
import rpg.rpg_class as rpg_class
import rpg.player_class as player_class
import rpg.classes as classes


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
            sheet_name="RPG", included=("items", "enemies", "rooms")
        )
        for function_ in (self.load_items, self.load_rooms):
            function_(named_ranges, sheets)

    def load_rooms(self, named_ranges, sheets):
        # TODO: make 1 function for this instead of copying load_items
        room_data = sheets.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=named_ranges["rooms"]
        ).execute()
        field_names, *room_data = room_data.get("values", [])
        # TODO: don't hardcode column order
        rpg_class.RPG.rooms.update({
            name: classes.Room(
                can_rest=utils.default(can_rest, False), level=level,
                enemies_list=[
                    classes.Enemy(name=enemy_name, level=int(level))
                    for enemy_name in enemies
                    if enemy_name
                ],
                boss=None if not boss_name else classes.Enemy(
                    name=boss_name, attack=int(boss_attack), defense=int(boss_defense),
                ), drops=drops
            )
            for name, can_rest, level, *enemies,
            boss_name, boss_attack, boss_defense, drops in room_data
        })

    def load_items(self, named_ranges, sheets):
        item_data = sheets.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=named_ranges["items"]
        ).execute()
        field_names, *item_data = item_data.get("values", [])
        rpg_class.RPG.all_items.update({
            item[0]: classes.Item(
                **{
                    name: data
                    for name, data in dict(zip(field_names, item)).items()
                    if data
                }
            ) for item in item_data if item
        })

    def save_game(self):
        """saves the game"""
        utils.save(rpg_players=self.game.players)
        player_class.players = self.game.players
