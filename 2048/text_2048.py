"""
A text=based clone of 2048
Made by Chendi
"""

import random
import json

games = {"current game": None}
save_file = "games_2048.json"


def newline(text, number=1):
    """adds number newlines to the end of text"""
    return text.strip() + ("\n" * number)


def get_item_safe(sequence, index=0, default=""):
    """
    Retrives the item at index in sequence
    defaults to default if the item des not exist
    """
    try:
        item = sequence[index]
    except IndexError:
        item = default
    return item


def clean(text):
    """cleans user input and returns as a list"""
    if text:
        if type(text) == str:
            return text.strip().lower().split()
        elif type(text) == list:
            return text
    else:
        return [""]


def trim(text, number=1, default=[""]):
    """
    trims the front of a sequence by number
    returns default if number is greater than len(sequence)
    """
    if type(text) == str:
        text = clean(text)
    if type(text) == list:
        for i in range(number):
            try:
                text = text[number:]
            except IndexError:
                text = default
                break
        return text
    else:
        return["something is wrong"]


def get_key(dictionary, item, *ignore):
    dictionary = dictionary.copy()
    for key in ignore:
        try:
            del dictionary[key]
        except KeyError:
            pass
    key_index = list(dictionary.values()).index(item)
    return list(dictionary.keys())[key_index]


class Cell():
    """represents a cell in a board"""

    def __init__(self, value=0):
        self.length = 1
        self.value = value
        self.has_merged = False


class Board():
    """represents a board for 2048"""
    def __init__(self, mode, values=None):
        self.size = mode.size
        self.number_of_cells = self.size ** 2
        if not values:
            values = [0 for i in range(self.number_of_cells)]
        self.cells = [Cell(value) for value in values]

    def move_blocks(self, x, positive, game):
        """Moves all blocks in the board"""
        # generates indexes of cell for each row/column
        for i in range(self.size):
            if x:
                indexes = list(range(i * self.size, (i + 1) * self.size))
            else:
                indexes = list(range(i, self.number_of_cells, self.size))
            if positive:
                indexes.reverse()

            for j in indexes:
                current_cell = self.cells[j]
                current_cell.has_merged = False
                neighbor = self.cells[indexes[indexes.index(j) - 1]]

                if current_cell.value > 0:
                    while current_cell is not self.cells[indexes[0]]:
                        # moves if neighbor is empty
                        if neighbor.value == 0:
                            neighbor.value = current_cell.value
                            neighbor.has_merged = current_cell.has_merged
                            current_cell.value = 0
                            j = indexes[indexes.index(j) - 1]
                            current_cell = self.cells[j]
                            neighbor = self.cells[indexes[indexes.index(j) - 1]]
                        # merges blocks
                        elif (
                                current_cell.value == neighbor.value and not
                                current_cell.has_merged and not neighbor.has_merged
                                ):
                            current_cell.value += 1
                            game.score += game.mode.increase_score(current_cell.value)
                            neighbor.value = 0
                            current_cell.has_merged = True
                        else:
                            break

    def check_can_move(self):
        """Checks if the player can move"""
        if not self.check_full():
            return True

        # checks if adjacent cells are the same
        for i in range(self.size):
            row_indexes = list(range(i * self.size, i * self.size + self.size))
            column_indexes = list(range(i, self.number_of_cells, self.size))
            for indexes in (row_indexes, column_indexes):
                for j in indexes:
                    if j is indexes[0]:
                        continue
                    elif self.cells[j].value == self.cells[indexes[indexes.index(j) - 1]].value:
                        return True
        return False

    def check_full(self):
        """Checks if the board is full"""
        for cell in self.cells:
            if cell.value == 0:
                return False
        return True

    def make_new_block(self, mode):
        """Makes random new block"""
        if self.check_full():
            return
        empty_blocks = [cell for cell in self.cells if cell.value == 0]
        empty_cell = random.choice(empty_blocks)
        value = 1
        if random.randint(0, 10) == 10:
            value = 2
        empty_cell.value = value

    def draw_board(self, game):
        """appends the board to self.text"""
        max_length = 0
        for cell in self.cells:
            cell.length = len(str(game.mode.values[cell.value]))
            max_length = cell.length if cell.length > max_length else max_length
        max_length += 1
        for row in range(game.mode.size):
            for column in range(game.mode.size):
                cell = game.board.cells[row * game.mode.size + column]
                spaces = (max_length - cell.length) * " "
                game.text += spaces * 2 + str(game.mode.values[cell.value])
            game.text += "\n"


class GameMode():
    """class to represent different gamemodes"""
    shuffled = [i for i in range(100)]
    random.shuffle(shuffled)

    def __init__(
        self, start_value=2, increase_type="normal",
        size=4, win_value=11, description="", shuffled=False
            ):
        self.size = size
        self.number_of_cells = size ** 2
        self.increase_type = increase_type
        self.high_score = 0
        if shuffled:
            self.values = [0] + GameMode.shuffled
        else:
            self.values = [0, start_value]
            for i in range(self.number_of_cells + 2):
                self.values.append(self.increase(self.values[-1]))
        self.win_value = win_value
        self.description = description

    def increase(self, value):
        """Increases cell value based on game mode"""
        if self.increase_type == "normal":
            next_value = value * 2
        elif self.increase_type == "plus one":
            next_value = value + 1
        return next_value

    def increase_score(self, value):
        """increases score based on gamemode"""
        return 2 ** value


class Game():
    """class to represent each game of 2048"""
    modes = {
        "normal": GameMode(description="normal 2048"),
        "65536": GameMode(size=5, win_value=16, description="5x5 board and higher win condition"),
        str(2 ** 20): GameMode(size=6, win_value=20, description="6x6 board and higher win condition"),
        "eleven": GameMode(1, "plus one", description="blocks increase by 1 when merging"),
        "twenty": GameMode(1, "plus one", size=5, win_value=20, description="5x5 board with the rules of eleven"),
        "confusion": GameMode(1, "random", shuffled=True, description="randomly generated block sequence")
    }
    commands = {
        "restart": "restarts the game in the current gamemode",
        "gamemodes": "lists the gamemodes",
        "help": "prints this help text",
        "scores": "prints the highscore for each mode",
        "games": "prints all existing games, their mode and score",
        "reserved": "prints reserved words",
        "move": "prints valid <directions>"
    }
    help_text = (
        "this is a 2048 clone by chendi",
        "how to play:",
        "move the tiles",
        "when 2 with the same value touch, they merge",
        "try to get the highest value posible without filling up the board",
        "commands:",
        "prefix all commands with /2048",
        "playing 2048 will not interfere with other bot commands",
        "all commands must be spelled correctly but are NOT case-sensitive",
        "note that the current game and highscores are reset when the bot resets",
    )

    extra_commands = {
        "<direction> - move the tiles in the given direction (use move to see valid <directions>)"
        "create <game_name>": "creates a new game with the given name (can be combined with other commands",
        "<game_name>": "loads the game named game_name (can be combined with other commands)",
        "rename <old_name> <new_name>": "renames a game from old_name to new_name",
        "delete <game_name>": "deletes the game named game_name"
    }
    movement = {
        "up": ("up", "u", "^"), "left": ("left", "l", "<"),
        "down": ("down", "d", "v"), "right": ("right", "r", ">")
    }

    reserved_words = (
        list(commands.keys()) + list(modes.keys()) +
        [value for values in list(movement.values()) for value in values] +
        list(extra_commands.keys()) +
        ["2048", "/2048", "current game"]
    )

    def __init__(self, board=None, has_won=False, mode="normal", score=0):
        self.score = score
        self.text = ""
        self.mode = self.modes[mode]
        self.state = None
        self.has_won = has_won
        self.board = Board(self.mode, board)
        for i in range(2):
            self.board.make_new_block(self.mode)

    def update(self):
        """appends text based on current state"""

        if self.state == "help":
            self.text += newline("\n".join(self.help_text))
            for command, description in list(self.commands.items()) + list(self.extra_commands.items()):
                self.text += f"{command} - {description}\n"
            self.state = None

        if self.state == "won":
            self.has_won = True
            self.draw_game()
            self.text += "you won, use move to continue playing"
        elif self.state == "lost":
            self.text += "you lost, use restart to restart, or gamemodes to get a list of gamemodes"
        elif self.state == "restart":
            self.restart()
        elif self.state == "gamemodes":
            self.text += "pick a gamemode or continue playing\n"
            for mode_name, mode in self.modes.items():
                self.text += f"{mode_name} - {mode.description}\n"
        elif self.state == "scores":
            for mode_name, mode in self.modes.items():
                self.text += f"{mode_name}: {mode.high_score}\n"
        elif self.state == "reserved":
            self.text += ", ".join(Game.reserved_words)
        elif self.state == "games":
            for game_name, game in games.items():
                if game_name != "current game":
                    self.text += f"{game_name} - {get_key(Game.modes, game.mode)} score: {game.score}\n"
        elif self.state == "move":
            for direction, commands in Game.movement.items():
                command = ", ".join(commands)
                self.text += f"{direction} - {command}"
        self.state = None

        self.text = newline(self.text, 2)
        self.draw_game()

    def draw_game(self):
        """appends board and scores to self.text"""
        game_name = get_key(games, self, "current game")
        mode_name = get_key(Game.modes, self.mode)
        self.text += f"{game_name} - {mode_name}\n"
        self.text += "score: " + str(self.score) + "\n"
        self.board.draw_board(self)

    def restart(self, mode=None):
        """Resets the game"""
        self.mode = mode if mode else self.mode
        self.score = 0
        if self.mode == Game.modes["confusion"]:
            self.setup_confusion()
        self.board = Board(self.mode)
        for i in range(2):
            self.board.make_new_block(self.mode)
        self.state = None
        self.has_won = False

    def move(self, x, positive):
        """Moves all blocks"""
        if (x, positive) == (None, None):
            return
        if self.board.check_can_move():
            old_board_values = [cell.value for cell in self.board.cells]
            self.board.move_blocks(x, positive, self)

            # does not create new block if board is full or the board did not change
            if not self.board.check_full() and old_board_values != [cell.value for cell in self.board.cells]:
                self.board.make_new_block(self.mode)

        if self.score > self.mode.high_score:
            self.mode.high_score = self.score
        if not self.board.check_can_move():
            self.state = "lost"
        if self.state != "won":
            self.check_win()

    def check_win(self):
        """checks if the player has won"""
        for block in self.board.cells:
            if block.value == self.mode.win_value and not self.has_won:
                self.state = "won"

    def setup_confusion(self):
        """shuffled the values for conffusion mode"""
        GameMode.shuffled.remove(0)
        random.shuffle(GameMode.shuffled)
        GameMode.shuffled.insert(0, 0)
        Game.modes["confusion"].values = GameMode.shuffled

    def play_game(self, command_list):
        """runs the main game loop once"""
        self.text = ""
        command = get_item_safe(command_list)

        # check player movement
        command = get_item_safe(command_list)
        x = None
        positive = None
        if command in Game.movement["up"]:
            x = False
            positive = False
        elif command in Game.movement["left"]:
            x = True
            positive = False
        elif command in Game.movement["down"]:
            x = False
            positive = True
        elif command in Game.movement["right"]:
            x = True
            positive = True

        self.move(x, positive)
        if (x, positive) == (None, None):
            if command in self.modes.keys():
                self.restart(Game.modes[command])
            elif command in self.commands.keys():
                self.state = command
            elif command != "":
                self.text += "invalid command, use help to see commands\n"
                self.state = None

        self.update()
        return newline(self.text)


def create_game(game_name):
    """creates a new game in games dict"""
    games["current game"] = games[game_name] = Game()
    return games["current game"]


def verify_name(*names):
    for name in names:
        if name in Game.reserved_words:
            return "game names cannot be reserved words"
        elif not name:
            return "games must have names"
        elif name in games.keys():
            return "names must be unique, note that names are NOT case-sensitive"
    return "valid"


def run_game(commands=""):
    """runs the game based on commands"""
    global games
    command_list = clean(commands)
    command = get_item_safe(command_list)

    # processing commands
    if command == "/2048":
        command_list = trim(command_list)
        command = get_item_safe(command_list)
    if command == "create":
        command_list = trim(command_list)
        game_name = get_item_safe(command_list)
        valid = verify_name(game_name)
        if valid != "valid":
            return valid
        create_game(game_name)
        command_list = trim(command_list)
    elif command == "rename":
        command_list = trim(command_list)
        old_name = get_item_safe(command_list)
        command_list = trim(command_list)
        new_name = get_item_safe(command_list)
        command_list = trim(command_list)
        valid = verify_name(new_name)
        if valid != "valid":
            return valid
        if old_name not in games.keys():
            return "that game does not exist"
        games[new_name] = games.pop(old_name)
        game_name = new_name
        command_list = trim(command_list)
    elif command == "delete":
        command_list = trim(command_list)
        game_name = get_item_safe(command_list)
        if not game_name:
            return "you must give the name of the game"
        elif game_name not in games.keys():
            return "that game does not exist"
        if games["current game"] == games[game_name]:
            games["current game"] = None
        del games[game_name]
        return f"{game_name} deleted"

    elif command in games.keys():
        game_name = command
        games["current game"] = games[game_name]
        command_list = trim(command_list)
    else:
        game_name = "current game"
    if type(games[game_name]) == Game:
        return games[game_name].play_game(command_list)
    else:
        return "no game selected"


def load_games():
    """loads games from a json file"""
    global games
    with open(save_file, "r") as save_data:
        data = json.load(save_data)
    for game_name, game_data in data["games"].items():
        games[game_name] = Game(game_data["board"], game_data["has won"], game_data["mode"], game_data["score"])
    for mode_name, mode in Game.modes.items():
        mode.high_score = data["scores"][mode_name]


def save_games():
    """saves games to a json file"""
    global games
    games_dict = dict()
    for game_name, game in games.items():
        if game_name == "current game" or (game is None):
            continue
        games_dict[game_name] = {
            "board": [cell.value for cell in game.board.cells],
            "has won": game.has_won,
            "mode": get_key(Game.modes, game.mode),
            "score": game.score
        }
    high_scores = {mode_name: mode.high_score for mode_name, mode in Game.modes.items()}
    data = json.dumps({"games": games_dict, "scores": high_scores})
    with open(save_file, "w") as save_data:
        save_data.write(data)


# testing via console
if __name__ == "__main__":
    text = ""
    while True:
        game_text = run_game(text)
        print(game_text)
        text = clean(input("enter a command: "))
        if get_item_safe(text) == "break":
            break

