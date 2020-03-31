import random


class Cell():
    offset = 10

    def __init__(self, value=0):
        self.length = 1
        self.value = value
        self.has_merged = False


class Board():

    def __init__(self, mode):
        self.size = mode.size
        self.number_of_cells = self.size ** 2
        # creates empty board and adds 2 random blocks
        self.cells = [Cell() for i in range(self.number_of_cells)]
        self.make_new_block(mode)
        self.make_new_block(mode)

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
                            current_cell.value = game.mode.increase(current_cell.value)
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
                    if self.cells[j].value == self.cells[indexes[indexes.index(j) - 1]].value:
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
        empty_blocks = [cell for cell in self.cells if cell.value == 0]
        empty_cell = random.choice(empty_blocks)
        if random.randint(0, 10) == 10:
            value = mode.values[1]
        else:
            value = mode.values[0]
        empty_cell.value = value

    def draw_board(self, game):
        """Draws the board"""
        max_length = 0
        for cell in self.cells:
            cell.length = len(str(cell.value))
            max_length = cell.length if cell.length > max_length else max_length
        for row in range(game.mode.size):
            for column in range(game.mode.size):
                cell = game.board.cells[row * 4 + column]
                game.text += " " * (max_length - cell.length) + str(cell.value) + " " * (max_length - cell.length)
            game.text += "\n"


class GameMode():

    def __init__(
        self, mode, start_value=2, increase_type="normal",
        size=4, win_value=None, values=None, colors=Cell.colors
            ):
        self.size = size
        self.number_of_cells = size ** 2
        self.increase_type = increase_type
        self.high_score = 0
        if values:
            self.values = values
        else:
            self.values = [start_value]
            for i in range(12):
                self.values.append(self.increase(self.values[-1]))
        self.win_value = win_value if win_value else self.values[10]

    def increase(self, value):
        """Increases cell value based on game mode"""
        if self.increase_type == "normal":
            next_value = value * 2
        elif self.increase_type == "plus one":
            next_value = value + 1
        elif self.increase_type == "random":
            next_value = self.values[self.values.index(value) + 1]

        return next_value

    def increase_score(self, value):
        if self.increase_type == "normal":
            points = value
        elif self.increase_type == "plus one":
            points = 2 ** value
        elif self.increase_type == "random":
            points = 2 ** (self.values.index(value) + 1)

        return points


class Game():
    shuffled = [i for i in range(100)]
    random.shuffle(shuffled)
    modes = {
        "normal": GameMode("normal"),
        "65536": GameMode("65536", size=5, win_value=65536),
        str(2 ** 20): GameMode(str(2 ** 20), size=6, win_value=2 ** 20),
        "eleven": GameMode("eleven", 1, "plus one"),
        "twenty": GameMode("twenty", 1, "plus one", win_value=20),
        "confusion": GameMode("confusion", 1, "random", values=shuffled)
    }
    commands = ["restart", "menu", "quit", "help"]

    def __init__(self):
        self.score = 0
        self.text = ""
        self.mode = self.modes["normal"]
        self.state = "menu"
        self.board = Board(self.mode)

    def update(self):
        """Draws based on current state"""
        if self.state == "playing":
            self.draw_game()
        elif self.state == "menu":
            self.text = "menutexthere"

        elif self.state == "won":
            self.draw_game()
            self.text += "You won! Use command move to continue playing."
            self.state = "playing"

        elif self.state == "lost":
            self.text = "You lost. Use command restart to restart, or command menu to change modes"

        elif self.state == "restart":
            self.restart()
        elif self.state == "help":
            self.text = (
                "How to Play:\n" +
                "Move the tiles. When 2 with the same value touch, they merge.\
                Try to get the highest value posible without filling up the board\n\n" +

                "prefix all commands with 2048 all commands must be spelled correctly and are case-sensitive" +
                "help - prints this help text\n\n" +
                "quit - ends the game and exits 2048 (high-scores will not be saved)\n\n" +

                "Play Mode Commands:\n" +
                "move <direction> - move the tiles in the given direction (eg. move up) can be abbreviated (eg. m u)\n" +
                "restart - restarts the game in the current gamemode\n" +
                "menu - go back to the menu (Changes mode to Menu)\n" +


                "Menu Commands:\n" +
                "note that these all refer to gamemodes and start a new game upon selection" +
                "normal - normal 2048\n" +
                "65536 - normal 2048 with a 5x5 board and higher win condition" +
                "eleven - instead of doubling, the blocks increase by 1 when merging" +
                "twenty - the rules of eleven and the board of 65536" +
                "confusion - randomly generated block sequences and colors"
            )
        elif self.state == "quit":
            self.text = "Thanks for playing!\nMade by Chendi"

    def draw_game(self):
        """Draws board and scores"""
        self.text += "Score: " + str(self.score) + "\nHigh Score: " + self.mode.high_score + "\n"
        self.board.draw_board(self)

    def restart(self, mode=None):
        """Resets the game"""
        self.mode = mode if mode else self.mode
        self.score = 0
        self.state = "playing"
        if self.mode == Game.modes["confusion"]:
            self.setup_confusion()
        self.board = Board(self.mode)

    def move(self, x, positive):
        """Moves all blocks"""
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
        for block in self.board.cells:
            if block.value == self.mode.win_value:
                self.state = "won"

    def setup_confusion(self):
        random.shuffle(self.shuffled)
        Game.modes["confusion"].win_value = Game.modes["confusion"].values[10]


def play_game(command_list):

    game = Game()

    # main game loop
    while game.state != "quit":

        game.text = ""

        command = command_list[0]
        # check player movement
        if game.state == "playing":
            if command in ("move", "m"):
                command = command_list[1]
                if command in ("up", "u"):
                    x = False
                    positive = False
                elif command in ("left", "l"):
                    x = True
                    positive = False
                elif command in ("down", "d"):
                    x = False
                    positive = True
                elif command in ("right", "r"):
                    x = True
                    positive = True
                else:
                    game.text = "Invalid move"
                game.move(x, positive)
            elif command in Game.commands:
                game.state = command

            else:
                game.text = "Invalid command. You are in Play Mode. Use help to learn more"

        elif game.state == "menu":
            if command in game.modes.keys:
                game.restart(Game.modes[command])
            elif command in ("help", "quit"):
                game.state = command

        game.update()
        yield game.text


if __name__ == "__main__":
    while True:
        text = input().lower().split()
        if text[0] == "break":
            break
        play_game(text)
