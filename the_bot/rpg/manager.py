"""
manager for rpg
"""
from datetime import datetime
import random
import utils
import rpg.classes as classes


class RPGManager:
    """manager for rpg"""

    save_file = "data.json"
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )
    game = classes.RPG()

    def __init__(self):
        self.commands = {
            "register": self.register,
            "inventory": self.inventory,
            "warp": self.warp,
            "equipped": self.equipped,
            "stats": self.stats,
            "rest": self.rest,
            "fight": self.fight,
            "atk": self.atk,
            "heal": self.heal
        }
        self.admin_commands = {
            "remove": self.remove,
            "sync": self.sync,
            "save_data": self.save_data,
            "set": self.set_,
        }

        self.data = utils.load(self.save_file)
        self.userData = self.data["users"]

        random.seed(datetime.now())

    def register(self):
        """registers a user"""
        pass

    def run_game(self, bot, user, conv, commands):
        """runs the game"""
        userID = user.id_[0]
        command = next(commands)
        if not command:
            return "you must enter a command"

        elif command not in list(self.commands) + list(self.admin_commands):
            return "That command doesn't exist!"

        elif command != "register" and userID not in classes.RPG.users:
            return "You are not registered! Use register"

        if command in self.admin_commands and not utils.userIn(self.admins, userID):
            return "bro wtf u cant use that"

        return self.commands[command](user, commands)
        self.save_game()

    def load_game(self):
        """loads the game"""
        pass

    def save_game(self):
        """saves the game"""
        save_data = self.game.players.copy()

        for userID, player in save_data:
            save_data[userID] = player.to_dict()

        utils.save(self.save_file, save_data)
        print("Successfully saved!")

    def sync(self, userID, commands):
        """syncs value to save_file"""
        key, value = utils.get_item_safe(commands, (0, 1))

        if value.isdigit():
            value = int(value)

        for player in self.userData:
            self.userData[player][key] = value

        self.save_game(self.save_file, self.data)

        return "Synced all values!"

    def remove(self, userID, commands):
        """removes a key from data"""
        key = next(commands)

        for user in self.userData:
            self.userData[user].pop(key, None)

        self.save_game(self.save_file, self.data)

        return "Removed key!"

    def set_(self, userID, commands):
        """sets a value"""
        userID, key, value = utils.get_item_safe(commands, (0, 1, 2))

        if value.isdigit():
            value = int(value)

        if userID in self.userData:
            self.userData[userID][key] = value

            utils.save(self.save_file, self.data)

            return "Set value!"
        else:
            return "That user isn't registered!"
