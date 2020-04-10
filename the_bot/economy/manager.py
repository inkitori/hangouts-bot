"""
manager for economy
"""
import economy.classes as classes
import classes.shop as shop
import utils


class EconomyManager():
    """manager for economy"""

    save_file = "the_bot/economy/save_data.json"

    def __init__(self):
        self.load_game()
        self.users = classes.users

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        output_text = ""
        if command == "register":
            self.register(userID, commands)
        elif userID not in self.users:
            return "You are not registered! Use register"

        user = self.users[userID]
        if command == "leaderboard":
            output_text = self.leaderboard()
        elif command == "shop":
            output_text = self.shop()
        elif command == "give":
            output_text = self.give(user, commands)
        elif command == "profile":
            output_text = self.profile(commands)
        elif command == "mine":
            output_text = user.mine()
        elif command == "buy":
            output_text = user.buy(commands)
        elif command == "prestige":
            output_text = user.prestige()
        elif command == "prestige_confirm":
            output_text = user.prestige_confirm()
        elif command == "prestige_cancel":
            output_text = user.prestige_cancel()

        return output_text

    def leaderboard(self):
        """returns leaderboard"""
        user_balances = {user: user.lifetime_balance for user in self.users}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [(key, value) for key, value in sorted(user_balances.items(), key=lambda x: x[1], reverse=True)]

        for rank in range(5):
            user, balance = sorted_users[rank]
            leaderboard_text += f"{rank + 1}. {user.name()}: {balance}\n"

        return leaderboard_text

    def shop(self):
        """returns shop"""
        shop_text = ""
        for type_ in shop:
            for item in type_:
                shop_text += f"{item.name()} - {item.price} Saber Dollars"
        return shop_text

    def save_game(self):
        """saves the game"""
        data = {player.__dict__ for player in self.users}
        utils.save(self.save_file, data)

    def load_game(self):
        """loads the game"""
        data = utils.load(self.save_file)
        for userID, user_data in data.items():
            self.users[userID] = classes.EconomyUser(
                name=user_data["name"],
                balance=user_data["balance"],
                lifetime_balance=user_data["lifetime_balance"],
                prestige=user_data["prestige"],
                items=user_data["items"],
                confirmed_prestige=user_data["confirmed_prestige"],
                prestige_upgrade=user_data["prestige_upgrade"],
            )

    def register(self, userID, commands):
        """registers a user"""
        name = next(commands)
        if not name:
            return "you must provide a name"
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
            if reciveing_user == user.name:
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

        for user in self.users:
            if user_name in user.name:
                possible_users.append(user)

        if not possible_users:
            return "No users go by that name!"

        elif len(possible_users) > 1:
            output_text += f"{len(possible_users)} user(s) go by that name:\n"

        for user in possible_users:
            output_text += user.profile()
        return utils.newline(output_text)
