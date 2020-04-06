import economy.classes as classes
import utils


class EconomyManager():

    picks = {
        "Tin": 100,
        "Iron": 250,
        "Lead": 625,
        "Silver": 1565,
        "Tungsten": 3910,
        "Gold": 9775,
        "Platinum": 24440,
        "Molten": 61100,
        "Cobalt": 152750,
        "Palladium": 381875,
        "Mythril": 954687,
        "Orichalcum": 2386717,
        "Adamantite": 5966792,
        "Titanium": 14916980,
        "Chlorophyte": 37292450,
        "Spectre": 93231125,
        "Luminite": 233077812,
    }
    users = {}

    def __init__(self):
        pass

    def run_game(self, bot, user, conv, commands):
        if userID not in self.users:
            return "You are not registered! Use /register"

        # use commands

    def leaderboard(self, bot, event):
        user_balances = {user: user.lifetime_balance for user in self.users}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [(key, value) for key, value in sorted(user_balances.items(), key=lambda x: x[1], reverse=True)]

        for rank in range(5):
            user, balance = sorted_users[rank]
            leaderboard_text += f"{rank + 1}. {user.name}: {balance}\n"

        return leaderboard_text

    def shop(self):
        with open("text/shop.txt", "r") as shop_text:
            return shop_text.read()

    def save_game(self):
        utils.save(self.save_file, self.data)

    def load_game(self):
        pass
        
    def register(self, userID):
        if userID in self.users:
            return "You are already registered!"
        try:
            users[userID] = classes.User()
            return "Successfully registered!"
        except Exception as e:
            return "Failed to register!"
            print(e)

    def profile(self):
        output_text = ""

        try:
            if len(event.text.split()) > 1:
                name = event.text.split(' ', 1)[1]
                possible_users = []

                for user in self.data["users"]:
                    if name in self.data["users"][user]["name"]:
                        possible_users.append(user)

                if len(possible_users) == 0:
                    return "No users go by that name!"
                    return

                elif len(possible_users) > 1:
                    output_text += f"{len(possible_users)} user(s) go by that name:\n"

                    for user in possible_users:
                        output_text += utils.join_items(
                            f"**Name:** {dataUsers[user]["name"]}"",  # multiple users
                            f"**Balance:** {dataUsers[user]["balance"]}",
                            f"**Pick:** {dataUsers[user]["pick"]}",
                            f"**Prestige:** {dataUsers[user]["prestige"]}",
                            f"**Prestige Level:** {dataUsers[user]["prestige_upgrade"]}",
                            f"**ID:** {user}"
                        )
                else:
                    conv.send_message(toSeg(
                        "**Name:** " + dataUsers[possible_users[0]]["name"] + '\n' +  # single user
                        "**Balance:** " + str(dataUsers[possible_users[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[possible_users[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[possible_users[0]]["prestige"]) + '\n' +
                        "**Prestige Level:** " + str(dataUsers[possible_users[0]]["prestige_upgrade"]) + '\n' +
                        "**ID:** " + possible_users[0])
                    )

            else:
                if user.id_[0] in self.data["users"]:
                    conv.send_message(toSeg(
                        "**Name:** " + self.data["users"][user.id_[0]]["name"] + '\n' +  # no args
                        "**Balance:** " + str(self.data["users"][user.id_[0]]["balance"]) + '\n' +
                        "**Pick:** " + dataUsers[user.id_[0]]["pick"] + '\n' +
                        "**Prestige:** " + str(dataUsers[user.id_[0]]["prestige"]) + '\n' +
                        "**Prestige Level:** " + str(dataUsers[user.id_[0]]["prestige_upgrade"]) + '\n' +
                        "**ID:** " + user.id_[0])
                    )
        except Exception as e:
            output_text += "Failed to retrieve user info!"
            print(e)

        return utils.newline(output_text)
