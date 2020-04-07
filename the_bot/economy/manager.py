"""
manager for economy
"""
import economy.classes as classes
import classes.shop as shop
import utils


class EconomyManager():
    """manager for economy"""

    users = {}

    def __init__(self):
        pass

    def run_game(self, bot, user, conv, commands):
        """runs the game"""
        userID = user.id_[0]
        if userID not in self.users:
            return "You are not registered! Use /register"
        command = next(commands)

        # use commands

    def leaderboard(self, bot, event):
        """returns leaderboard"""
        user_balances = {user: user.lifetime_balance for user in self.users}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [(key, value) for key, value in sorted(user_balances.items(), key=lambda x: x[1], reverse=True)]

        for rank in range(5):
            user, balance = sorted_users[rank]
            leaderboard_text += f"{rank + 1}. {user.name}: {balance}\n"

        return leaderboard_text

    def shop(self):
        """returns shop"""
        shop_text = ""
        for type_ in shop:
            for item in type_:
                shop_text += f"{item.name} - {item.price} Saber Dollars"
        return shop_text

    def save_game(self):
        """saves the game"""
        utils.save(self.save_file, self.data)

    def load_game(self):
        """loads the game"""
        pass

    def register(self, userID):
        """registers a user"""
        if userID in self.users:
            return "You are already registered!"
        self.users[userID] = classes.User()
        return "Successfully registered!"

    def give(self, giving_user, commands):
        """gives money to another user"""
        reciveing_user = next(commands)
        money = next(commands)
        output_text = ""

        if not reciveing_user:
            output_text = "You must specfiy a user or ID"
        elif not money:
            output_text = "You must specify an amount"

        for user in self.users.values():
            if reciveing_user in user.name:
                reciving_user = user
                break

        if reciveing_user in self.users:
            reciving_user = self.users[reciveing_user]
        elif reciving_user.id_[0] not in self.users:
            output_text = "That user has not registered!"
        elif reciving_user.id_[0] == giving_user.id_[0]:
            output_text = "That user is you!"

        if money < 0:
            output_text = "You can't give negative money!"
        elif user.change_balance < money:
            output_text = "You don't have enough money to do that!"
        else:
            giving_user.change_balance(- money)
            reciveing_user.change_balance(money)

            output_text = utils.join_items(
                f"Successfully given {money} Saber Dollars to {reciving_user.name}.",
                f"That user now has {reciveing_user.balance} Saber Dollars."
            )
        return output_text

    def profile(self, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_users = []

        for user in self.data["users"].values():
            if user_name in user.name:
                possible_users.append(user)

        if not possible_users:
            return "No users go by that name!"

        elif len(possible_users) > 1:
            output_text += f"{len(possible_users)} user(s) go by that name:\n"

        for user in possible_users:
            output_text += user.profile()

        return utils.newline(output_text)
