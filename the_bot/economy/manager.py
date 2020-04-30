"""
manager for economy
"""
import economy.classes as classes
import utils
import game_functions


class EconomyManager:
    """manager for economy"""

    def __init__(self):
        self.players = classes.players
        self.load_game()
        self.save_game()

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
        for type_name, items in classes.shop_items.items():
            items_text = [type_name]
            player_item = player.items[type_name]
            if player_item == len(items):
                items_text = f"You already have the highest level {type_name}"
            else:
                for i in range(player_item + 1, len(items)):
                    item = items[i]
                    items_text.append(utils.description(
                        item.name().title(),
                        f"{item.price} saber dollars"
                    ))
            shop_list.append(items_text)

        return utils.join_items(*shop_list, is_description=True, description_mode="long")

    def save_game(self):
        """saves the game"""
        utils.save(economy_players=self.players)
        classes.players = self.players

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
        self.players[player_id] = classes.EconomyPlayer(name=name)
        return "Successfully registered!"

    commands = {
        "leaderboard": leaderboard,
        "shop": shop,
        "profile": game_functions.profile
    }
    help_text = utils.join_items(
        ("informational", *commands, "help"),
        ("commands", *classes.EconomyPlayer.commands),
        is_description=True, description_mode="long"
    )
