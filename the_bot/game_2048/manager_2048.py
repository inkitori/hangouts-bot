"""
manager for 2048 games
"""
import json
import utils
from game_2048.game import Game


class Manager:
    games = {"current game": None}
    save_file = "the_bot/game_2048/save_data.json"

    def __init__(self):
        self.load_games()
        self.text = ""

    def create_game(self, game_name):
        """creates a new game in games dict"""
        self.games["current game"] = self.games[game_name] = Game()
        return self.games["current game"]

    def verify_name(self, *names):
        for name in names:
            if name in Game.reserved_words:
                return "game names cannot be reserved words"
            elif not name:
                return "games must have names"
            elif name in self.games.keys():
                return "names must be unique, note that names are NOT case-sensitive"
        return "valid"

    def run_game(self, commands=""):
        """runs the game based on commands"""
        output_text = ""
        command_list = utils.clean(commands)
        command = utils.get_item_safe(command_list)

        # processing commands
        if command == "/2048":
            command_list = utils.trim(command_list)
            command = utils.get_item_safe(command_list)

        if command == "create":
            command_list = utils.trim(command_list)
            game_name = utils.get_item_safe(command_list)
            valid = self.verify_name(game_name)
            if valid != "valid":
                output_text = valid
            self.create_game(game_name)
            command_list = utils.trim(command_list)

        elif command == "rename":
            command_list = utils.trim(command_list)
            old_name = utils.get_item_safe(command_list)
            command_list = utils.trim(command_list)
            new_name = utils.get_item_safe(command_list)
            command_list = utils.trim(command_list)
            valid = self.verify_name(new_name)
            if valid != "valid":
                output_text = valid
            if old_name not in self.games.keys():
                output_text = "that game does not exist"
            self.games[new_name] = self.games.pop(old_name)
            game_name = new_name
            command_list = utils.trim(command_list)

        elif command == "delete":
            command_list = utils.trim(command_list)
            game_name = utils.get_item_safe(command_list)
            if not game_name:
                output_text = "you must give the name of the game"
            elif game_name not in self.games.keys():
                output_text = "that game does not exist"
            if self.games["current game"] == self.games[game_name]:
                self.games["current game"] = None
            del self.games[game_name]
            output_text = f"{game_name} deleted"

        elif command == "games":
            for game_name, game in self.games.items():
                if game_name != "current game":
                    output_text = f"{game_name} - {utils.get_key(Game.modes, game.mode)} score: {game.score}\n"

        elif command in self.games.keys():
            game_name = command
            self.games["current game"] = self.games[game_name]
            command_list = utils.trim(command_list)
        else:
            game_name = "current game"
        if not output_text:
            if type(self.games[game_name]) == Game:
                output_text = self.games[game_name].play_game(command_list)
            else:
                output_text = "no game selected"
        save_games()
        return output_text

    def load_games(self):
        """loads games from a json file"""
        data = utils.load(self.save_file)
        for game_name, game_data in data["games"].items():
            self.games[game_name] = Game(game_data["board"], game_data["has won"], game_data["mode"], game_data["score"])
        for mode_name, mode in Game.modes.items():
            mode.high_score = data["scores"][mode_name]

    def save_games(self):
        """saves games to a json file"""
        games_dict = dict()
        for game_name, game in self.games.items():
            if game_name == "current game" or (game is None):
                continue
            games_dict[game_name] = {
                "board": [cell.value for cell in game.board.cells],
                "has won": game.has_won,
                "mode": utils.get_key(Game.modes, game.mode),
                "score": game.score
            }
        high_scores = {mode_name: mode.high_score for mode_name, mode in Game.modes.items()}
        data = json.dumps({"games": games_dict, "scores": high_scores})
        utils.save(self.save_file, data)
