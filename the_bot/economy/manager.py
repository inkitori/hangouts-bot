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

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        output_text = ""
        if command == "help":
            return "help text"
        if command == "register":
            return self.register(userID, commands)
        elif userID not in self.users.keys():
            return "You are not registered! Use register"

        user = self.users[userID]
        if command not in ("prestige", "prestige_upgrade"):
            user.confirmed_prestige = False
            user.confirmed_upgrade = False
        if command == "leaderboard":
            output_text = self.leaderboard()
        elif command == "shop":
            output_text = self.shop(user)
        elif command == "give":
            output_text = self.give(user, commands)
        elif command == "profile":
            output_text = self.profile(commands)
        elif command == "mine":
            output_text = user.mine()
        elif command == "buy":
            output_text = user.buy(commands)

        elif command == "prestige":
            output_text = user.prestige_action()
        elif command == "prestige_upgrade":
            output_text = user.prestige_upgrade_action()
        else:
            output_text = "Invalid command"

        return output_text

    def leaderboard(self):
        """returns leaderboard"""
        user_balances = {user: user.lifetime_balance for user in self.users.values()}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [(key, value) for key, value in sorted(user_balances.items(), key=lambda x: x[1], reverse=True)]

        for rank in range(5):
            user, balance = utils.get_item_safe(sorted_users, (rank, ))
            if user:
                leaderboard_text += f"{rank + 1}. {user.name}: {balance}\n"

        return leaderboard_text

    def shop(self, user):
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
                    items_text.append(utils.description(item.name().title(), f"{item.price} saber dollars"))
            shop_list.append(items_text)

        return utils.join_items(*shop_list, is_description=True, description_mode="long")

    def save_game(self):
        """saves the game"""
        data = {userID: player.__dict__ for userID, player in self.users.items()}
        utils.save(self.save_file, data)

    def load_game(self):
        """loads the game"""
        data = utils.load(self.save_file)
        for userID, user_data in data.items():
            self.users[int(userID)] = classes.EconomyUser(
                name=user_data["name"],
                balance=user_data["balance"],
                lifetime_balance=user_data["lifetime_balance"],
                prestige=user_data["prestige"],
                items=user_data["items"],
            )

    def register(self, userID, commands):
        """registers a user"""
        name = next(commands)
        if userID in self.users:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.users[userID] = classes.EconomyUser(name)
        return "Successfully registered!"

    def give(self, giving_user, commands):
        """gives money to another user"""
        reciveing_user = next(commands)
        money = next(commands)
        output_text = ""

        if not reciveing_user:
            output_text += "You must specfiy a user or ID"
        elif not money:
            output_text += "You must specify an amount"
        elif not money.isdigit():
            output_text += "You must give an integer amount of Saber Dollars"
        else:
            money = int(money)

            for user in self.users.values():
                if reciveing_user == user.name:
                    reciveing_user = user
                    break

            if reciveing_user.isdigit() and int(reciveing_user) in self.users:
                reciveing_user = self.users[int(reciveing_user)]
            if reciveing_user.id() not in self.users:
                output_text += "That user has not registered!"
            elif reciveing_user.id() == giving_user.id():
                output_text += "That user is you!"
            else:
                if money < 0:
                    output_text += "You can't give negative money!"
                elif giving_user.balance < money:
                    output_text += "You don't have enough money to do that!"
                else:
                    giving_user.change_balance(- money)
                    reciveing_user.change_balance(money)

                    output_text += utils.join_items(
                        f"Successfully given {money} Saber Dollars to {reciveing_user.name}.",
                        f"That user now has {reciveing_user.balance} Saber Dollars."
                    )
        return output_text

    def profile(self, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_users = []

        for user in self.users.values():
            if user_name in user.name:
                possible_users.append(user)
        if user_name.isdigit() and int(user_name) in self.users:
            possible_users.append(self.users[int(user_name)])
        if not possible_users:
            output_text += "No users go by that name!"

        elif len(possible_users) > 1:
            output_text += f"{len(possible_users)} user(s) go by that name:\n"

        for user in possible_users:
            output_text += user.profile()
        return utils.newline(output_text)
