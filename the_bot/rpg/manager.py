"""
manager for rpg
"""
import datetime
import random

import rpg.classes as classes
import rpg.player_class as player_class
import rpg.rpg_class as rpg_class
import utils


class RPGManager:
    """manager for rpg"""
    game = rpg_class.RPG()
    spreadsheet_id = "1H9m57A7vcSvGnEIrAKAHjg-GmvKw1GqQqQdAMeuN5do"

    def __init__(self, load_sheets=True):
        self.load_game(load_sheets=load_sheets)
        random.seed(datetime.datetime.now())
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
        self.game.players, player_class.parties = utils.load("rpg_players", "rpg_parties")
        if load_sheets:
            self.load_sheets_data()

    def load_sheets_data(self):
        data = {"rooms": self.load_rooms, "items": self.load_items}
        sheets = utils.create_sheets_service().spreadsheets()
        named_ranges = utils.get_named_ranges(
            sheets, spreadsheet_id=self.spreadsheet_id,
            sheet_name="RPG", included=data.keys()
        )
        for range_name, function_ in data.items():
            fields, *game_data = sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=named_ranges[range_name]
            ).execute().get("values", [])
            function_(fields, game_data)

    def load_rooms(self, fields, room_data):
        # TODO: don't hardcode column order
        rpg_class.RPG.rooms.update({
            name: classes.Room(
                can_rest=utils.default(can_rest, False), level=int(level),
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

    def load_items(self, fields, item_data):
        """loads items from google sheets"""
        rpg_class.RPG.all_items.update({
            item[0].lower(): classes.Item(
                **{
                    name: data
                    for name, data in dict(zip(fields, item)).items()
                    if data
                }
            ) for item in item_data if item
        })

    def save_game(self):
        """saves the game"""
        utils.save(rpg_players=self.game.players, rpg_parties=player_class.parties)
        player_class.players = self.game.players
