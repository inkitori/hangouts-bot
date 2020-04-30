"""
manager for 2048 games
"""
import utils
import game_2048.classes as classes


class Manager2048:
    """manager for 2048 game"""
    game_management_commands = [
        "create {game_name}", "{game_name}", "rename {old_name} {new_name}",
        "delete {game_name}", "games",
    ]
    reserved_words = (
        classes.Game.game_commands + list(classes.Game.modes.keys()) +
        [command for direction in classes.Directions for command in direction.value.commands] +
        game_management_commands +
        ["2048", "/2048"] + [keyword.value for keyword in classes.Keywords]
    )
    reserved_words = [
        word
        for words in reserved_words
        for word in words.split()
        if not word.startswith("{")
    ]
    help_texts = {
        "help": "",  # avoids probelems with referencing itself
        "gamemodes": utils.join_items(
            *[
                (mode_name, mode.description)
                for mode_name, mode in classes.Game.modes.items()
            ],
            description_mode="short"
        ),
        "move": utils.join_items(
            *[
                (direction.name.lower(), *direction.value.commands)
                for direction in classes.Directions
            ],
            description_mode="short"
        ),
        "scores": utils.join_items(
            *[
                (mode_name, mode.high_score)
                for mode_name, mode in classes.Game.modes.items()
            ],
            description_mode="short"
        ),
        "reserved": utils.description("reserved", *reserved_words)
    }
    help_texts["help"] = utils.join_items(
        ("in-game commands", *list(classes.Game.game_commands)),
        ("game management", *game_management_commands),
        ("informational", *list(help_texts)),
        description_mode="long"
    )
    # needs to be here because resereved_words is declared first (avoid circular references)
    reserved_words += list(help_texts)
    games = classes.games

    def __init__(self):
        self.load_game()
        self.save_game()

    def update_high_scores(self):
        self.help_texts["scores"] = utils.join_items(
            *[
                (mode_name, mode.high_score)
                for mode_name, mode in classes.Game.modes.items()
            ],
            description_mode="short"
        )

    def create_game(self, game_name):
        """creates a new game in games dict"""
        self.games[game_name] = classes.Game()
        return self.games[game_name]

    def verify_name(self, *names):
        """verifies a name for a game"""
        for name in names:
            if name in self.reserved_words:
                return "game names cannot be reserved words"
            elif not name:
                return "games must have names"
            elif name in self.games.keys():
                return "names must be unique, note that names are NOT case-sensitive"
        return "valid"

    def run_game(self, user, commands):
        """runs the game based on commands"""
        # TODO: clean this mess up
        output_text = ""
        command = next(commands)
        play_game_name = ""

        # processing commands
        if command == "create":
            new_game_name = next(commands)
            valid = self.verify_name(new_game_name)
            if valid != "valid":
                return valid
            self.create_game(new_game_name)
            play_game_name = new_game_name

        elif command == "rename":
            old_name = next(commands)
            new_name = next(commands)

            valid = self.verify_name(new_name)
            if valid != "valid":
                return valid
            elif old_name not in self.games.keys():
                return "that game does not exist"

            self.games[new_name] = self.games.pop(old_name)
            play_game_name = new_name
            output_text = f"renamed {old_name} to {new_name}"

        elif command == "delete":
            output_text = self.delete_game(commands)

        elif command in self.games:
            self.games[classes.Keywords.CURRENT_GAME] = self.games[command]

        elif command == "games":
            output_text += utils.newline(utils.default(utils.join_items(
                *[
                    utils.description(
                        game_name, game.mode_name, game.score)
                    for game_name, game in self.games.items()
                    if game_name != classes.Keywords.CURRENT_GAME
                ], 
            ), "there are no games"), 2)

        elif command in self.help_texts:
            output_text += self.help_texts[command]

        else:
            # moves the generator back one command because the command was not used
            commands.send(-1)

        play_game_name = utils.default(
            play_game_name, classes.Keywords.CURRENT_GAME)
        self.games[classes.Keywords.CURRENT_GAME] = self.games[play_game_name]

        if output_text:
            return output_text

        # plays game
        if self.games[classes.Keywords.CURRENT_GAME]:
            output_text = self.games[classes.Keywords.CURRENT_GAME].play_game(
                commands)
        else:
            output_text = "no game selected"

        self.update_high_scores()
        return output_text

    def load_game(self):
        """loads games from file"""
        self.games, scores = utils.load("games_2048", "scores_2048")
        for mode_name, mode in classes.Game.modes.items():
            mode.high_score = scores[mode_name]

    def save_game(self):
        """saves games to a json file"""
        scores = {
            mode_name: mode.high_score
            for mode_name, mode in classes.Game.modes.items()
        }
        utils.save(games_2048=self.games, scores_2048=scores)
        classes.games = self.games

    def delete_game(self, commands):
        """deletes a game"""
        delete_game_name = next(commands)
        if not delete_game_name:
            return "you must give the name of the game"
        elif delete_game_name not in self.games.keys():
            return "that game does not exist"
        else:
            if self.games[classes.Keywords.CURRENT_GAME] == self.games[delete_game_name]:
                self.games[classes.Keywords.CURRENT_GAME] = None
            del self.games[delete_game_name]
            return f"{delete_game_name} deleted"
