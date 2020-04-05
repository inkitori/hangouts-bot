from collections import defaultdict
from datetime import datetime
import math
import random
import utils
import rpg.classes


class RPGManager:

    save_file = "data.json"
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    game = Game()

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

    # rpg
    def run_game(self, userID, event_text):
        commands = clean(event_text)
        commands = trim(commands)
        command = get_item_safe(commands)
        if not command:
            return "you must enter a command"

        elif command not in list(self.commands) + list(self.admin_commands):
            return "That command doesn't exist!"

        elif command != "register" and userID not in users:
            return "You are not registered! Use register"

        user = self.users[userID]
        commands = trim(commands)

        if command in self.admin_commands and not userIn(self.admins, userID):
            return "bro wtf u cant use that"

        return self.commands[command](user, commands)
        save(self.save_file, self.data)

    def fight(self, user, commands):
        rooms = self.data["rooms"]
        text = ""

        player_room = user.room

        # DO NOT let an if elif chain happen here
        if player_room == "village":
            return "Don't fight in the village..."

        elif user.fighting:
            return f"You are already fighting {user.fighting}!"

        else:
            enemy = random.choice(rooms[player_room].enemies_list)

            text += f"{enemy} has approached to fight!\n"
            text += enemy.stats.print_stats()
            user.fighting = enemy
            return text

    def attack(self, user, commands):
        text = ""

        if not user.fighting:
            return "You need to be in a fight!"

        else:
            enemy = enemies[user.fighting]
            user_damage = user.modified_stats().attack
            damage_dealt = (user_damage) * (user_damage / enemy.defense)

            multiplier = random.choice((1, -1))
            damage_dealt += int(multiplier * math.sqrt(damage_dealt / 2))
            enemy.stats.health -= damage_dealt

            text += f"You dealt {damage_dealt} damage to {enemy.name}!\n"

            if enemy.stats.health <= 0:
                text += f"{enemy.name} is now dead!\n"

                xp_range = rooms[user.room].xp_range
                xp_earned = random.randint(*xp_range)

                gold_earned = int(enemy.max_health / 10) + random.randint(1, 10)

                text += f"You earned {xp_earned} xp and {gold_earned} gold!"
                text += user.stats.give_xp(userID, xp_earned)

                user.stats.increase_balance(gold_earned)

                user.fighting = ""
                return text

            # take damage
            damage_taken = enemy.attack / user.modified_stats().defense

            multiplier = random.choice((1, -1))
            damage_taken += int(multiplier * math.sqrt(damage_taken / 2))

            user.health -= damage_taken

            text += join_list(
                f"{enemy.name} dealt {damage_taken} to you!",
                f"You have {user.stats.hp} hp left",
                f"{enemy.name} has {enemy.stats.health} left!"
            )

            save(self.save_file, self.data)
            if user.stats.health <= 0:
                text += f"You were killed by {enemy.name}..."

                user.fighting = ""
                user.stats.change_health("full")

            return text

    def load_game():
        pass

    def save_game(self, userID, commands):
        save(self.save_file, self.data)
        return "Successfully saved!"

    def sync(self, userID, commands):
        key, value = get_item_safe(commands, (0, 1))

        if value.isdigit():
            value = int(value)

        for user in self.userData:
            self.userData[user][key] = value

        save(self.save_file, self.data)

        return "Synced all values!"

    def remove(self, userID, commands):
        key = get_item_safe(commands)

        for user in self.userData:
            self.userData[user].pop(key, None)

        save(self.save_file, self.data)

        return "Removed key!"

    def set_(self, userID, commands):
        userID, key, value = get_item_safe(commands, (0, 1, 2))

        if value.isdigit():
            value = int(value)

        if userID in self.userData:
            self.userData[userID][key] = value

            save(self.save_file, self.data)

            return "Set value!"
        else:
            return "That user isn't registered!"
