
import rpg.player_class as player_class
import rpg.classes as classes
import utils


class RPG():
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

    def register(self, user_ID, commands):
        """registers a user in the game"""
        name = next(commands)
        if user_ID in self.players:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.players[user_ID] = player_class.Player(name=name)
        return "Successfully registered!"

    def profile(self, player, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_players = []

        for possible_player in self.players.values():
            if user_name in possible_player.name:
                possible_players.append(possible_player)
        if user_name.isdigit() and int(user_name) in self.players:
            possible_players.append(self.players[int(user_name)])
        elif user_name == "self":
            possible_players.append(player)
        if not possible_players:
            output_text += "No users go by that name!"

        elif len(possible_players) > 1:
            output_text += f"{len(possible_players)} player(s) go by that name:\n"

        for user in possible_players:
            output_text += user.print_profile()
        return utils.newline(output_text)

    def play_game(self, user_ID, commands):
        """runs functions based on user command"""
        command = next(commands)
        output_text = ""
        player = utils.get_value(self.players, user_ID)
        if command == "register":
            output_text = self.register(user_ID, commands)
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
            output_text = player_class.Inventory.commands[command](player.inventory, commands)
        elif command in player_class.Player.commands:
            output_text = player_class.Player.commands[command](player, commands)
        else:
            output_text = "invalid command for rpg"

        return output_text
