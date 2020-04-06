"""
manager for economy
"""
import economy.classes as classes
import classes.items as items
import utils


class EconomyManager():
    """manager for economy"""

    users = {}

    def __init__(self):
        pass

    def run_game(self, bot, user, conv, commands):
        """runs the game"""
        if userID not in self.users:
            return "You are not registered! Use /register"

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
        with open("text/shop.txt", "r") as shop_text:
            return shop_text.read()

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
        try:
            users[userID] = classes.User()
            return "Successfully registered!"

    def give(self, giving_user, commands):
        """gives money to another user"""
        reciveing_user = next(commands)
        money = next(commands)

        if not reciveing_user:
            return "You must specfiy a user or ID"
        elif not money:
            return "You must specify an amount"

        for user in users.values():
            if reciveing_user in user.name:
                reciving_user = user
                break

        if reciveing_user in self.users:
            reciving_user = self.users[reciveing_user]
        elif reciving_user.id_[0] not in self.users:
            return "That user has not registered!"
        elif reciving_user.id_[0] == giving_user.id_[0]:
            return "That user is you!"

        if money < 0:
            return "You can't give negative money!"
        elif user.change_balance < money:
            return "You don't have enough money to do that!"
        else:
            giving_user.change_balance(- money)
            reciveing_user.change_balance(money)

            return utils.join_items(
                f"Successfully given {money} Saber Dollars to {reciving_user.name}.",
                f"That user now has {reciveing_user.balance} Saber Dollars."
            )

    def profile(self, commands):
        """returns user profiles"""
        output_text = ""

        try:
            if len(event.text.split()) > 1:
                name = event.text.split(' ', 1)[1]
                possible_users = []

                for user in self.data["users"].values():
                    if name in user.name:
                        possible_users.append(user)

                if len(possible_users) == 0:
                    return "No users go by that name!"

                elif len(possible_users) > 1:
                    output_text += f"{len(possible_users)} user(s) go by that name:\n"

                for user in possible_users:
                    output_text += user.profile()

            elif user.id_[0] in self.users:
                output_text += users[user.id_[0]].profile()
        except Exception as e:
            output_text += "Failed to retrieve user info!"
            print(e)

        return utils.newline(output_text)
