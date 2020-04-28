"""
manager for economy
"""
import economy.classes as classes
import utils


class EconomyManager():
    """manager for economy"""

    save_file = "the_bot/economy/save_data.json"

    def __init__(self):
        self.users = classes.users
        self.load_game()
        self.commands = {
            "leaderboard": self.leaderboard,
            "shop": self.shop,
            "profile": self.profile
        }
        self.help_text = utils.join_items(
            ("informational", *self.commands, "help"),
            ("commands", *classes.EconomyUser.commands),
            is_description=True, description_mode="long"
        )
        self.save_game()

    def run_game(self, user_id, commands):
        """runs the game"""
        command = next(commands)
        output_text = ""
        if command == "help":
            return self.help_text
        if command == "register":
            return self.register(user_id, commands)
        elif user_id not in self.users.keys():
            return "You are not registered! Use register"

        user = self.users[user_id]
        if command not in ("prestige", "prestige_upgrade"):
            user.confirmed_prestige = False
            user.confirmed_upgrade = False
        if command in self.commands:
            function_ = self.commands[command]
            output_text = function_(user, commands)
        elif command in classes.EconomyUser.commands:
            function_ = classes.EconomyUser.commands[command]
            output_text = function_(user, commands)
        else:
            output_text = "Invalid command"

        return output_text

    def leaderboard(self, playing_user, commands):
        """returns leaderboard"""
        user_balances = {user: user.lifetime_balance for user in self.users.values()}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [
            user for user in sorted(
                list(user_balances.items()),
                key=lambda x: x[1], reverse=True
            )
        ]

        for rank in range(5):
            user_balance = utils.get_item(sorted_users, (rank, ))
            if user_balance:
                user, balance = user_balance
                leaderboard_text += f"{rank + 1}. {user.name}: {balance}\n"

        playing_user_rank = sorted_users.index((playing_user, playing_user.lifetime_balance))
        if playing_user_rank > 5:
            leaderboard_text += (
                f"\n{playing_user_rank + 1}."
                f"{playing_user.name}(you): {playing_user.lifetime_balance}"
            )

        return leaderboard_text

    def shop(self, user, commands):
        """returns shop"""
        shop_list = []
        for type_name, items in classes.shop_items.items():
            items_text = [type_name]
            player_item = user.items[type_name]
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
        utils.save(economy_users=self.users)
        classes.users = self.users

    def load_game(self):
        """loads the game"""
        self.users = utils.load("economy_users")

    def register(self, user_id, commands):
        """registers a user"""
        name = next(commands)
        if user_id in self.users:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.users[user_id] = classes.EconomyUser(name=name)
        return "Successfully registered!"

    def profile(self, user, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_users = []

        for possible_user in self.users.values():
            if user_name in possible_user.name:
                possible_users.append(possible_user)
        if user_name.isdigit() and int(user_name) in self.users:
            possible_users.append(self.users[int(user_name)])
        elif user_name == "self":
            possible_users.append(user)
        if not possible_users:
            output_text += "No users go by that name!"

        elif len(possible_users) > 1:
            output_text += f"{len(possible_users)} user(s) go by that name:\n"

        for user in possible_users:
            output_text += user.profile()
        return utils.newline(output_text)
