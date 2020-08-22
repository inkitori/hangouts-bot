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

        return utils.join_items(*shop_list, description_mode="long")

    def give(self, player, commands):
        """gives money to another player"""
        # input validation
        receiving_player = next(commands)
        money = next(commands)
        if not money:
            return "You must specify an amount"
        elif not money.isdigit():
            return "You must give an integer amount of Saber Dollars"

        money = int(money)
        # get the player
        receiving_player = self.get_player(receiving_player)
        if type(receiving_player) == str:
            return receiving_player
        if receiving_player.id_ == player.id_:
            return "That player is you!"

        # check money is valid
        if money < 0:
            return "You can't give negative money!"
        elif player.balance < money:
            return "You don't have enough money to do that!"

        player.change_balance(-money)
        receiving_player.change_balance(money)

        return utils.join_items(
            f"Successfully given {money} Saber Dollars to {receiving_player.name}.",
            f"{receiving_player.name} now has {receiving_player.balance} Saber Dollars."
        )

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
        self.players[player_id] = classes.EconomyPlayer(id_=player_id, name=name)
        return "Successfully registered!"

    commands = {
        "leaderboard": leaderboard,
        "shop": shop,
        "profile": game_utils.profile,
        "give": give,
    }
    help_text = utils.join_items(
        ("commands", *classes.EconomyPlayer.commands, *commands, "help"),
        description_mode="long"
    )
