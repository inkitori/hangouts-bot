"""
A text based clone of 2048
Made by Chendi
"""
import random
import utils
import enum
import collections


@enum.unique
class Keywords(enum.Enum):
    """this just exists because spelling errors"""
    CURRENT_GAME = "current game"


class Cell:
    """represents a cell in a board"""

    def __init__(self, value=0):
        self.length = 1
        self.value = value
        self.has_merged = False


class Board:
    """represents a board for 2048"""

    def __init__(self, mode):
        self.size = mode.size
        self.number_of_cells = self.size ** 2
        self.cells = [Cell() for _ in range(self.number_of_cells)]

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
            self.move_line(indexes, game)

    def move_line(self, line, game):
        for j in line:
            current_cell = self.cells[j]
            current_cell.has_merged = False
            neighbor = self.cells[line[line.index(j) - 1]]

            if current_cell.value:
                while current_cell is not self.cells[line[0]]:
                    # moves if neighbor is empty
                    if not neighbor.value:
                        neighbor.value = current_cell.value
                        neighbor.has_merged = current_cell.has_merged
                        current_cell.value = 0
                        j = line[line.index(j) - 1]
                        current_cell = self.cells[j]
                        neighbor = self.cells[line[line.index(j) - 1]]
                    # merges blocks
                    elif (
                        current_cell.value == neighbor.value and not
                        current_cell.has_merged and not neighbor.has_merged
                    ):
                        current_cell.value += 1
                        game.score += game.mode().increase_score(current_cell.value)
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
            cell.length = len(str(game.mode().values[cell.value]))
            max_length = max(self.cells, key=lambda cell: cell.value).value
        max_length += 1
        for row in range(game.mode().size):
            for column in range(game.mode().size):
                cell = game.board.cells[row * game.mode().size + column]
                spaces = (max_length - cell.length + 1) * " "
                game.text += spaces * 2 + str(game.mode().values[cell.value])
            game.text += "\n"


@enum.unique
class GameIncreaseModes(enum.Enum):
    TIMES_2 = enum.auto()
    PLUS_1 = enum.auto()
    RANDOM = enum.auto()


class GameMode:
    """class to represent different gamemodes"""
    shuffled = [i for i in range(100)]
    random.shuffle(shuffled)

    def __init__(
        self, start_value=2, increase_type=GameIncreaseModes.TIMES_2,
        size=4, win_value=11, description=""
    ):
        self.size = size
        self.number_of_cells = size ** 2
        self.increase_type = increase_type
        self.high_score = 0
        if increase_type == GameIncreaseModes.RANDOM:
            self.values = [0] + GameMode.shuffled
        else:
            self.values = [0, start_value]
            for _ in range(self.number_of_cells + 2):
                self.values.append(self.increase(self.values[-1]))
        self.win_value = win_value
        self.description = description

    def name(self):
        return utils.get_key(Game.modes, self, is_same=False)

    def increase(self, value):
        """Increases cell value based on game mode"""
        if self.increase_type == GameIncreaseModes.TIMES_2:
            next_value = value * 2
        elif self.increase_type == GameIncreaseModes.PLUS_1:
            next_value = value + 1
        return next_value

    def increase_score(self, value):
        """increases score based on gamemode"""
        return 2 ** value


Direction = collections.namedtuple("Direction", "commands x positive")


@enum.unique
class Directions(enum.Enum):
    UP = Direction(("up", "u", "^"), False, False)
    LEFT = Direction(("left", "l", "<"), True, False)
    DOWN = Direction(("down", "d", "v"), False, True)
    RIGHT = Direction(("right", "r", ">"), True, True)


class Game:
    """class to represent each game of 2048"""
    modes = {
        "normal": GameMode(description="normal 2048"),
        "65536": GameMode(size=5, win_value=16, description="5x5 board"),
        str(2 ** 20): GameMode(size=6, win_value=20, description="6x6 board"),
        "eleven": GameMode(
            1, GameIncreaseModes.PLUS_1,
            description="blocks increase by 1 when merging"
        ),
        "twenty": GameMode(
            1, GameIncreaseModes.PLUS_1, size=5, win_value=20,
            description="eleven with a 5x5 board"
        ),
        "confusion": GameMode(
            1, GameIncreaseModes.RANDOM,
            description="randomly generated block sequence"
        )
    }
    game_commands = ["restart", "{direction}"]

    def __init__(self):
        self.score = 0
        self.text = ""
        self.mode_name = "normal"
        self.state = None
        self.has_won = False
        self.board = Board(self.mode())
        for _ in range(2):
            self.board.make_new_block(self.mode())

    def name(self):
        """name of the game"""
        return utils.get_key(games, self, Keywords.CURRENT_GAME)

    def mode(self):
        return self.modes[self.mode_name]

    def update(self):
        """appends text based on current state"""
        if self.state == "won":
            self.has_won = True
            self.draw_game()
            self.text += "you won"
        elif self.state == "lost":
            self.text += "you lost, use restart to restart, or gamemodes to get a list of gamemodes"
        elif self.state == "restart":
            self.restart()
        self.state = None

        self.text = utils.newline(self.text, 2)
        self.draw_game()

    def draw_game(self):
        """appends board and scores to self.text"""
        self.text += utils.join_items(
            utils.description(self.name(), self.mode().name()),
            f"score: {self.score}",
            end="\n" * 2
        )
        self.board.draw_board(self)

    def restart(self, mode=None):
        """Resets the game"""
        self.mode_name = utils.default(mode, self.mode_name)
        self.score = 0
        if self.mode_name == "confusion":
            self.setup_confusion()
        self.board = Board(self.mode())
        for _ in range(2):
            self.board.make_new_block(self.mode())
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
                self.board.make_new_block(self.mode())

        if self.score > self.mode().high_score:
            self.mode().high_score = self.score
        if not self.board.check_can_move():
            self.state = "lost"
        if self.state != "won":
            self.check_win()

    def check_win(self):
        """checks if the player has won"""
        for block in self.board.cells:
            if block.value == self.mode().win_value and not self.has_won:
                self.state = "won"

    def setup_confusion(self):
        """shuffled the values for conffusion mode"""
        GameMode.shuffled.remove(0)
        random.shuffle(GameMode.shuffled)
        GameMode.shuffled.insert(0, 0)
        Game.modes["confusion"].values = GameMode.shuffled

    def play_game(self, commands):
        """runs the main game loop once"""
        self.text = ""
        command = next(commands)

        # check player movement
        x = None
        positive = None
        for direction in Directions:
            direction = direction.value
            if command in direction.commands:
                self.move(direction.x, direction.positive)
                break
        else:
            if (x, positive) == (None, None):
                if command in self.modes:
                    self.restart(command)
                elif command in self.game_commands and not command.startswith("{"):
                    self.state = command
                elif command != "":
                    self.text += "invalid command, use help to see commands\n"
                    self.state = None

        self.update()
        return utils.newline(self.text)


games = {Keywords.CURRENT_GAME: None}
