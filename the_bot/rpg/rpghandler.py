from collections import defaultdict
from datetime import datetime
import json  # u shouldn't need this cause its in utils.py
import math
import random
from utils import *
from the_bot.rpg.rpg_classes import *


class RPGHandler:

    save_file = "the_bot/data.json"
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    users = {}
    rooms = {"village": Room()}
    enemies = {}

    def __init__(self):
        self.commands = {
            "register": self.register,
            "inventory": self.inventory,
            "warp": self.warp,
            "equipped": self.equipped,
            "stats": self.stats,
            "rest": self.rest,
            "xp": self.xp,
            "fight": self.fight,
            "atk": self.atk,
            "heal": self.heal
        }
        self.admin_commands = {
            "remove": self.remove,
            "sync": self.sync,
            "save_data": self.save_data,
            "set": self.set,
        }

        self.cooldowns = defaultdict(dict)

        self.data = utils.load(self.save_file)
        self.userData = self.data["users"]

        random.seed(datetime.now())

    # rpg
    def rpg_process(self, userID, event_text):
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

    def register(self, user, commands):
        userID = get_key(self.users, user)
        if userID in self.users:
            return "You are already registered!"
        self.users[userID] = Player("placeholder name")

        return "Successfully registered!"

    def warp(self, user, commands):
        inv = ""
        rooms = self.data["rooms"]
        users = self.userData
        room = get_item_safe(commands)
        if not room:
            return "Invalid argument! use warp {room}"

        if self.fighting:
            return "You can't warp while in a fight!"

        elif room not in rooms:
            return "That room doesn't exist!"

        elif rooms[room]["required_lvl"] > users[userID]["lvl"]:
            return "Your level is not high enough to warp there!"

        elif room == user.room:
            return "You are already in that room!"

        user.room = room
        return "Successfully warped!"

    def fight(self, user, commands):
        rooms = self.data["rooms"]
        text = ""

        player_room = self.room

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

            health_text = (
                f"{enemy.name} dealt {damage_taken} to you!",
                f"You have {user.stats.hp} hp left",
                f"{enemy.name} has {enemy.stats.health} left!"
            )
            text += "\n".join(health_text)

            save(self.save_file, self.data)
            if user.stats.health <= 0:
                text += f"You were killed by {enemy.name}..."

                user.died()

            return text

    def rest(self, user, commands):
        text = ""
        if user.room == "village":
            user.stats.full_health()
            text += "You feel well rested...\n"
            text += f"Your health is back up to {user.stats.hp}!"
        else:
            text = "You have to rest in the village!"

        return text

    def save_data(self, userID, commands):
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

    def set(self, userID, commands):
        userID, key, value = get_item_safe(commands, (0, 1, 2))

        if value.isdigit():
            value = int(value)

        if userID in self.userData:
            self.userData[userID][key] = value

            save(self.save_file, self.data)

            return "Set value!"
        else:
            return "That user isn't registered!"
