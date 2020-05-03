
import rpg.player_class as player_class
import rpg.inventory_class as inventory_class
import rpg.classes as classes
import utils
import game_utils


class RPG:
    """the RPG"""
    all_items = classes.all_items
    players = player_class.players
    rooms = classes.rooms

    def __init__(self):
        # nothing to put here right now
        pass

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

    def play_game(self, player_id, commands):
        """runs functions based on player command"""
        command = next(commands)
        output_text = ""
        player = self.players.get(player_id, None)
        if command == "register":
            output_text = self.register(player_id, commands)
        elif command == "help":
            output_text = utils.join_items(
                ("inventory", *inventory_class.Inventory.commands),
                ("player", "register", "profile", *player_class.Player.commands),
                ("other", "help"),
                ("combat", *player_class.Player.fight_commands),
                ("party", *player_class.Player.party_commands),
                description_mode="long"
            )
        elif command == "profile":
            output_text = game_utils.profile(self, player, commands)

        elif command in inventory_class.Inventory.commands:
            output_text = inventory_class.Inventory.commands[command](
                player.inventory, commands)
        elif command in player_class.Player.commands:
            output_text = player_class.Player.commands[command](
                player, commands
            )
        elif command in player_class.Player.fight_commands:
            output_text = player.fight_action(
                player_class.Player.fight_commands[command], commands
            )
        elif command in player_class.Player.party_commands:
            output_text = player_class.Player.party_commands[command](
                player, commands
            )
        else:
            output_text = "invalid command for rpg"

        return output_text
