"""
manager for 2048 games
"""
import utils
from game_2048.classes import Game


class Manager2048:
    """manager for 2048 game"""
    games = {"current game": None}
    save_file = "the_bot/game_2048/save_data.json"

    def __init__(self):
        self.load_game()

    def create_game(self, game_name):
        """creates a new game in games dict"""
        self.games[game_name] = Game()
        return self.games[game_name]

    def verify_name(self, *names):
        """verifies a name for a game"""
        for name in names:
            if name in Game.reserved_words:
                return "game names cannot be reserved words"
            elif not name:
                return "games must have names"
            elif name in self.games.keys():
                return "names must be unique, note that names are NOT case-sensitive"
        return "valid"

    def run_game(self, user, commands):
        """runs the game based on commands"""
        output_text = ""
        command = next(commands)
        play_game_name = ""

        # processing commands
        if command == "create":
            new_game_name = next(commands)
            valid = self.verify_name(new_game_name)
            if valid != "valid":
                output_text = valid
            self.create_game(new_game_name)
            play_game_name = new_game_name

        elif command == "rename":
            old_name = next(commands)
            new_name = next(commands)
            valid = self.verify_name(new_name)
            if valid != "valid":
                output_text = valid
            if old_name not in self.games.keys():
                output_text = "that game does not exist"
            self.games[new_name] = self.games.pop(old_name)
            play_game_name = new_name
            output_text = f"renamed {old_name} to {new_name}"

        elif command == "delete":
            delete_game_name = next(commands)
            if not delete_game_name:
                output_text = "you must give the name of the game"
            elif delete_game_name not in self.games.keys():
                output_text = "that game does not exist"
            else:
                if self.games["current game"] == self.games[delete_game_name]:
                    self.games["current game"] = None
                del self.games[delete_game_name]
                output_text = f"{delete_game_name} deleted"

        elif command == "games":
            for game_name, game in self.games.items():
                if game_name != "current game":
                    output_text += utils.description(game_name, game.mode.name(), game.score)  # f"{game_name} - {game.mode.name()} score: {game.score}\n"

        elif command in self.games:
            play_game_name = command
            self.games["current game"] = self.games[play_game_name]

        elif command == "gamemodes":
            output_text += "pick a gamemode or continue playing\n"
            output_text += utils.join_items(
                *[(mode_name, mode.description) for mode_name, mode in Game.modes.items()],
                is_description=True
            )
        elif command == "scores":
            output_text += utils.join_items(
                *[(mode_name, mode.high_score) for mode_name, mode in Game.modes.items()],
                is_description=True
            )
        elif command == "reserved":
            output_text += utils.join_items(*Game.reserved_words, seperator=", ")
        elif command == "move":
            output_text += utils.join_items(
                *[[direction] + list(commands) for direction, commands in Game.movement.items()],
                is_description=True
            )
        elif command == "help":
            output_text += utils.join_items(*list(Game.commands.items()) + list(Game.extra_commands.items()), is_description=True)

        if not play_game_name:
            play_game_name = "current game"
        else:
            self.games["current game"] = self.games[play_game_name]

        if not output_text:
            if type(self.games[play_game_name]) == Game:
                output_text = self.games[play_game_name].play_game(commands)
            else:
                output_text = "no game selected"
        return output_text

    def load_game(self):
        """loads games from a json file"""
        data = utils.load(self.save_file)
        for game_name, game_data in data["games"].items():
            self.games[game_name] = Game(game_data["board"], game_data["has won"], game_data["mode"], game_data["score"])
        for mode_name, mode in Game.modes.items():
            mode.high_score = data["scores"][mode_name]

    def save_game(self):
        """saves games to a json file"""
        games_dict = dict()
        for game_name, game in self.games.items():
            if game_name == "current game" or (game is None):
                continue
            games_dict[game_name] = {
                "board": [cell.value for cell in game.board.cells],
                "has won": game.has_won,
                "mode": game.mode.name(),
                "score": game.score
            }
        high_scores = {mode_name: mode.high_score for mode_name, mode in Game.modes.items()}
        data = {"games": games_dict, "scores": high_scores}
        utils.save(self.save_file, data)
