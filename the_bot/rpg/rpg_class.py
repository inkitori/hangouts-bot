
import rpg.player_class as player_class
import rpg.classes as classes
import utils


class RPG:
    """the RPG"""
    all_items = classes.all_items
    players = player_class.players
    rooms = classes.rooms
    enemies = classes.enemies

    def __init__(self):
        for room_name in self.rooms:
            for enemy_name in self.rooms[room_name].enemies_list:
                if enemy_name not in self.enemies:
                    print(f"invalid enemy {enemy_name} in room {room_name}")

    def register(self, player_id, commands):
        """registers a player in the game"""
        name = next(commands)
        if player_id in self.players:
            return "You are already registered!"

        # input validation
        if not name:
            return "you must provide a name"
        elif name in [player.name for player in self.players.values()]:
            return "that name is taken by a player"

        self.players[player_id] = player_class.Player(name=name)
        return "Successfully registered!"

    def profile(self, player, commands, players=None):
        """returns player profiles"""
        # TODO: get rid of self and just use players
        players = utils.default(players, self.players)
        output_text = ""
        player_name = next(commands)

        # create list of players
        possible_players = []
        for possible_player in players.values():
            if player_name in possible_player.name:
                possible_players.append(possible_player)
        if player_name.isdigit() and int(player_name) in players:
            possible_players.append(players[int(player_name)])
        elif player_name == "self":
            possible_players.append(player)

        if not possible_players:
            output_text += "No players go by that name/id!"

        elif len(possible_players) > 1:
            output_text += utils.newline(
                f"{len(possible_players)} player(s) go by that name:")

        output_text += utils.join_items(
            *[
                player.profile()
                for player in possible_players
            ], end="\n"
        )
        return output_text

    def play_game(self, player_id, commands):
        """runs functions based on player command"""
        command = next(commands)
        output_text = ""
        player = utils.get_value(self.players, player_id)
        if command == "register":
            output_text = self.register(player_id, commands)
        elif command == "help":
            output_text = utils.join_items(
                ("player_class.Inventory", *player_class.Inventory.commands),
                ("player", "register", "profile", *player_class.Player.commands),
                ("other", "help"),
                is_description=True, description_mode="long"
            )
        elif command == "profile":
            output_text = self.profile(player, commands)

        elif command in player_class.Inventory.commands:
            output_text = player_class.Inventory.commands[command](
                player.inventory, commands)
        elif command in player_class.Player.commands:
            output_text = player_class.Player.commands[command](
                player, commands)
        else:
            output_text = "invalid command for rpg"

        return output_text
