"""
A text based clone of 2048
Made by Chendi
"""
import random
import utils


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
        if self.number_of_empty_cells():
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

    def number_of_empty_cells(self):
        """Checks if the board is full and return number of empty spaces"""
        empty = 0
        for cell in self.cells:
            if cell.value == 0:
                empty += 1
        return empty

    def make_new_block(self, mode):
        """Makes random new block"""
        if not self.number_of_empty_cells():
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

    def name(self):
        return utils.get_key(Game.modes, self)

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
        "reserved": "prints reserved words",
        "move": "prints valid {directions}"
    }

    extra_commands = {
        "{direction}": "move the tiles in the given direction (use move to see valid {directions})",
        "create {game_name}": "creates a new game with the given name (can be combined with other commands).",
        "{game_name}": "loads the game named game_name (can be combined with other commands)",
        "rename {old_name} {new_name}": "renames a game from old_name to new_name",
        "delete {game_name}": "deletes the game named game_name",
        "games": "prints all existing games, their mode and score",
    }
    movement = {
        "up": ("up", "u", "^"), "left": ("left", "l", "<"),
        "down": ("down", "d", "v"), "right": ("right", "r", ">")
    }
    directions = {
        "up": (False, False), "left": (True, False),
        "down": (False, True), "right": (True, True)
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
        if self.board.number_of_empty_cells() == self.mode.number_of_cells and not score:
            for i in range(2):
                self.board.make_new_block(self.mode)

    def name(self):
        """name of the game"""
        return "placeholder, use command games to see games"
        # return utils.get_key(games, self)

    def update(self):
        """appends text based on current state"""

        if self.state == "help":
            self.text += utils.join_items(*list(self.commands.items()) + list(self.extra_commands.items()), is_description=True)
            self.state = None

        if self.state == "won":
            self.has_won = True
            self.draw_game()
            self.text += "you won"
        elif self.state == "lost":
            self.text += "you lost, use restart to restart, or gamemodes to get a list of gamemodes"
        elif self.state == "restart":
            self.restart()
        elif self.state == "gamemodes":
            self.text += "pick a gamemode or continue playing\n"
            self.text += utils.join_items(
                *[(mode_name, mode.description) for mode_name, mode in self.modes.items()],
                is_description=True
            )
        elif self.state == "scores":
            self.text += utils.join_items(
                *[(mode_name, mode.high_score) for mode_name, mode in self.modes.items()],
                is_description=True
            )
        elif self.state == "reserved":
            self.text += utils.join_items(*Game.reserved_words, seperator=", ")
        elif self.state == "move":
            self.text += utils.join_items(
                *[[direction] + list(commands) for direction, commands in Game.movement.items()],
                is_description=True
            )
        self.state = None

        self.text = utils.newline(self.text, 2)
        self.draw_game()

    def draw_game(self):
        """appends board and scores to self.text"""
        self.text += utils.description(self.name(), self.mode.name())
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
            if old_board_values != [cell.value for cell in self.board.cells]:
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

    def play_game(self, commands, command=""):
        """runs the main game loop once"""
        self.text = ""
        command = command if command else next(commands)

        # check player movement
        x = None
        positive = None
        for direction in self.movement:
            if command in self.movement[direction]:
                self.move(*self.directions[direction])
                break
        else:
            if (x, positive) == (None, None):
                if command in self.modes:
                    self.restart(Game.modes[command])
                elif command in self.commands:
                    self.state = command
                elif command != "":
                    self.text += "invalid command, use help to see commands\n"
                    self.state = None

        self.update()
        return utils.newline(self.text)
