"""
manager for economy
"""
import economy.classes as classes
import utils
import game_utils


class EconomyManager:
    """manager for economy"""

    def __init__(self):
        self.players = {}
        self.items = {
            "pick": classes.Item.generate_items(
                "pick", (
                    "copper", "tin", "iron", "lead", "silver", "tungsten", "gold", "platinum", "molten",
                    "cobalt", "palladium", "mythril", "orichalcum", "adamantite", "titanium",
                    "chlorophyte", "spectre", "luminite",
                ), (
                    0, 100, 250, 625, 1565, 3910, 9775, 24440, 61100, 152750, 381875, 954687,
                    2386717, 5966792, 14916980, 37292450, 93231125, 233077812,
                )
            )
        }
        self.load_game()
        self.save_game()

    def get_item(self, modifier, type_):
        if not modifier or not type_:
            return "Invalid item name"
        elif type_ not in self.items:
            return "That item doesn't exist!"
        items = self.items[type_]
        for item in items:
            if item.modifer == modifier:
                return item

        return "That item doesn't exist!"

    def run_game(self, player_id, commands):
        """runs the game"""
        command = next(commands)
        output_text = ""
        if command == "help":
            return self.help_text
        if command == "register":
            return self.register(player_id, commands)
        elif player_id not in self.players.keys():
            return "You are not registered! Use register"

        player = self.players[player_id]
        if command not in ("prestige", "prestige_upgrade"):
            player.confirmed_prestige = False
            player.confirmed_upgrade = False
        if command in self.commands:
            function_ = self.commands[command]
            output_text = function_(self, player, commands)
        elif command in classes.EconomyPlayer.commands:
            function_ = classes.EconomyPlayer.commands[command]
            output_text = function_(player, commands)
        else:
            output_text = "Invalid command"

        return output_text

    def get_player(self, name):
        if not name:
            return "You must specify a player or ID"
        for player in self.players.values():
            if name == player.name:
                return player
        if name.isdigit() and int(name) in self.players:
            return self.players[int(name)]
        return "Invalid player"

    def leaderboard(self, playing_player, commands):
        """returns leaderboard"""
        player_balances = {
            player: player.lifetime_balance for player in self.players.values()}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_players = [
            player for player in sorted(
                list(player_balances.items()),
                key=lambda x: x[1], reverse=True
            )
        ]

        for rank in range(5):
            player_balance = utils.get_item(sorted_players, (rank, ))
            if player_balance:
                player, balance = player_balance
                leaderboard_text += f"{rank + 1}. {player.name}: {balance}\n"

        playing_player_rank = sorted_players.index(
            (playing_player, playing_player.lifetime_balance))
        if playing_player_rank > 5:
            leaderboard_text += (
                f"\n{playing_player_rank + 1}."
                f"{playing_player.name}(you): {playing_player.lifetime_balance}"
            )

        return leaderboard_text

    def shop(self, player, commands):
        """returns shop"""
        shop_list = []
        for type_name, items in self.items.items():
            items_text = [type_name]
            player_item = player.get_item(type_name)
            if items.index(player_item) == len(items) - 1:
                items_text = f"You already have the highest level {type_name}"
            else:
                for item in items[items.index(player_item) + 1:]:
                    items_text.append(utils.description(
                        item.name().title(),
                        f"{item.price} saber dollars"
                    ))

            shop_list.append(items_text)

        return utils.join_items(*shop_list, description_mode="long")

    def save_game(self):
        """saves the game"""
        utils.save(economy_players=self.players)

    def load_game(self):
        """loads the game"""
        self.players = utils.load("economy_players")

    def register(self, player_id, commands):
        """registers a player"""
        name = next(commands)
        if player_id in self.players:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.players[player_id] = classes.EconomyPlayer(
            id_=player_id, name=name, manager=self)
        return "Successfully registered!"

    commands = {
        "leaderboard": leaderboard,
        "shop": shop,
        "profile": game_utils.profile,
    }
    help_text = utils.join_items(
        ("commands", *classes.EconomyPlayer.commands, *commands, "help"),
        description_mode="long"
    )
