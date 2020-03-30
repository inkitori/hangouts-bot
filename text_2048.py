import random
# import shelve
import pygame
import pygame.freetype
pygame.init()


class Cell(pygame.Rect):
    offset = 10

    def __init__(self, position, mode, value=0):
        self.value = value
        self.position = position
        self.has_merged = False
        super().__init__(x, y, width, height)

    def draw_value(self, font_size):
        """Draws the value of the block"""
        # print value


class Board():

    def __init__(self, mode):
        self.size = mode.size
        self.number_of_cells = self.size ** 2
        # creates empty board and adds 2 random blocks
        self.cells = [Cell(i, mode) for i in range(self.number_of_cells)]
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
        # dont forget to draw lines

        for cell in self.cells:
            if cell.value > 0:
                # add cell


class GameMode():

    def __init__(
        self, mode, start_value=2, increase_type="normal",
        size=4, win_value=None, values=None
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


class Menu():

    def __init__(self, button_list):
        self.buttons = []
        # create each button
        for button in button_list:
            self.buttons.append(button)
            print buttons if command lsit options


class Game():
    shuffled = [i for i in range(100)]
    random.shuffle(shuffled)
    modes = {
        "Normal": GameMode("Normal"),
        "65536": GameMode("65536", size=5, win_value=65536),
        str(2 ** 20): GameMode(str(2 ** 20), size=6, win_value=2 ** 20),
        "Eleven": GameMode("Eleven", 1, "plus one"),
        "Twenty": GameMode("Twenty", 1, "plus one", win_value=20),
        "Confusion": GameMode("Confusion", 1, "random", values=shuffled)
    }
    buttons = ("Restart", "Menu", "Quit")


    def __init__(self):
        self.score = 0
        self.mode = self.modes["Normal"]
        self.state = "Menu"
        self.board = Board(self.mode)
        self.main_menu = Menu(self.modes)
        self.game_menu = Menu(self.buttons)
        self.font.render_to(self.main_menu.surface, (300, 50), "2048", size=100)
        self.draw_end()

    def draw_end(self):
        end_text = ("Thanks for playing!\nMade by Chendi")
        # print end text to hangouts
    def update(self):
        """Draws based on current state"""
        wait = False
        if self.state == "Playing":
            self.draw_game()
        elif self.state == "Menu":
            self.window.blit(self.main_menu.surface, self.main_menu.window_position)

        elif self.state == "Won" or self.state == "Lost":
            won = self.state == "Won"
            self.draw_game()
            text = "You won!" if won else "You lost"
            # print text to hangouts
            if won:
                self.state = "Playing"

        elif self.state == "Restart":
            self.restart()

        elif self.state == "Quit":
            # print smth to hangouts

    def draw_game(self):
        """Draws board and scores"""
        self.board.draw_board(self)
        # prnt score
        # print high score
        # print game

    def restart(self, mode=None):
        """Resets the game"""
        self.mode = mode if mode else self.mode
        self.score = 0
        self.state = "Playing"
        if self.mode == Game.modes["Confusion"]:
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
            self.state = "Lost"
        if self.state != "Won":
            self.check_win()

    def check_win(self):
        for block in self.board.cells:
            if block.value == self.mode.win_value:
                self.state = "Won"

    def setup_confusion(self):
        random.shuffle(Cell.shuffled_colors)
        random.shuffle(self.shuffled)
        Game.modes["Confusion"].win_value = Game.modes["Confusion"].values[10]

def play_game(text):

    game = Game()

    # main game loop
    while game.state != "Quit":

        # event loop
            # check for quit

                game.state = "Quit"
                break

            # check player movement
            if game.state == "Playing":
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    x = False
                    positive = False
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    x = True
                    positive = False
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    x = False
                    positive = True
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    x = True
                    positive = True
                else:
                    continue
                game.move(x, positive)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                main_menu = game.state == "Menu"
                menu = game.main_menu if main_menu else game.game_menu
                for button in menu.buttons:
                    if command matches
                        if main_menu:
                            game.restart(Game.modes[button])
                        else:
                            game.state = button

        yield game.update()
