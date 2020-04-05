import economy.classes

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

    def leaderboard(self, bot, event):
        user, conv = getUserConv(bot, event)
        users = {}
        count = 1
        leaderboard = "Ranking by balanced earned in this lifetime:\n"

        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            for user in self.data["users"]:
                users[user] = (self.data["users"][user]["total_balance"])

            sorted_users = {key: value for key, value in sorted(users.items(), key=lambda x: x[1], reverse=True)}

            for key, value in sorted_users.items():
                if count == 6:
                    break

                leaderboard += str(count) + '. ' + self.data["users"][key]["name"] + ": " + str(value) + '\n'
                count += 1
            conv.send_message(toSeg(leaderboard))

        except:
            conv.send_message(toSeg("Failed retrieving leaderboard info!"))

    def shop(self, bot, event):
        user, conv = getUserConv(bot, event)

        if cooldown(self.cooldowns, user, event, 20):
            return

        try:
            with open("text/shop.txt", "r") as f:
                s = f.read()
                conv.send_message(toSeg(s))
        except:
            conv.send_message(toSeg("Failed to retrieve shop!"))
