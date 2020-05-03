import utils
import random
import math
import rpg.classes as classes
import rpg.inventory_class as inventory_class


class Player:
    """represents a player in the rpg"""

    def __init__(self, name):
        self.name = name
        self.stats = classes.Stats(
            attack=5, defense=5, speed=10, max_mana=100, mana=100,
            health=100, max_health=100, level=1, exp=0,
            balance=0, lifetime_balance=0
        )
        self.room = "village"
        self.args = {"autofight": False, "heal_percent": 50}
        self.inventory = inventory_class.Inventory()
        self.party = Party(self)

    def get_id(self):
        return utils.get_key(players, self)

    def modified_stats(self):
        """returns Stats() of player modified by player.equipped"""
        modifiers = self.inventory.modifers()
        modified_attack = modifiers.attack + self.stats.attack
        modified_defense = modifiers.defense + self.stats.defense
        return classes.Stats(attack=modified_attack, defense=modified_defense)

    def warp(self, commands):
        """warps to rooms"""
        output_text = ""
        rooms = classes.rooms
        room = next(commands)
        if not room:
            output_text = "Invalid argument! use warp {room}"
        elif self.party.fighting:
            output_text = "You can't warp while in a fight!"

        elif room not in rooms:
            output_text = "That room doesn't exist!"

        elif room == self.room:
            output_text = "You are already in that room!"
        else:
            self.room = room
            output_text = "Successfully warped!"
        return output_text

    def rest(self, commands):
        """rests player"""
        if classes.rooms[self.room].can_rest:
            self.stats.health = "full"
            # TODO: change mana to max
            text = utils.join_items(
                "You feel well rested...",
                f"Your health is back up to {self.stats.health}!",
            )
        else:
            text = "You can't rest here!"

        return text

    def heal(self, commands, enemy):
        """heal the player with their tome"""
        tome_name, tome = self.inventory.get_equipped(classes.ItemType.TOME)
        if not tome_name:
            return "you do not have a tome equipped"
        if self.stats.mana < tome.stats.mana:
            return "You do not have enough mana to heal!"
        else:
            self.stats.mana -= tome.stats.mana
            self.stats.health += tome.stats.health

            text = utils.newline(
                f"You have been healed back up to {self.stats.health}")

            if self.fighting:
                text += enemy.attack(self)

            return text

    def attack(self, commands, enemy):
        """attacks an enemy"""
        text = ""

        player_damage = self.modified_stats().attack + self.stats.attack
        damage_dealt = round(
            player_damage * (player_damage / enemy.stats.defense), 1
        )

        multiplier = random.choice((1, -1))
        damage_dealt += round(multiplier * math.sqrt(damage_dealt / 2), 1)
        damage_dealt = round(damage_dealt, 1)
        enemy.stats.health -= damage_dealt
        text += utils.newline(
            f"You dealt {damage_dealt} damage to {enemy.name}!")

        if enemy.stats.health <= 0:
            text += self.party.killed_enemy(enemy, self)

        else:
            # take damage
            text += enemy.attack(self)

            if self.stats.health <= 0:
                text += self.party.died(enemy, self)

        return text

    def fight_action(self, action, commands):
        """"""
        if not self.party.fighting:
            if not self.name == self.party.host.name:
                return "you are not in a fight. Only hosts may start fights"
            else:
                return self.fight(commands)
        if self.name is not self.party.doing_stuff:
            self.party.fight()
            return f"it is {self.party.doing_stuff}'s turn"
        output_text = action(self, commands, self.party.get_enemy())
        self.party.doing_stuff = None
        self.party.fight()

        return output_text

    def died(self, cause):
        text = utils.join_items(
            f"You were killed by {cause}...",
            "You woke up back in the village"
        )
        self.fighting = {}
        self.stats.health = "full"
        self.warp("village" for _ in range(1))
        return text

    def autofight(self, enemy_name, enemy):
        while True:
            # this might get deleted so leave it alone for now
            pass

    def set_(self, commands):
        arg = next(commands)
        value = next(commands)

        # input validation
        if arg not in self.args:
            return "That is not a valid arg!"
        elif not arg:
            return "you must provide an arg"
        elif not value:
            return "you must provide a value"

        elif isinstance(self.args[arg], bool):
            value = value[0]
            if value in ("t", "y"):
                self.args[arg] = True

            elif value in ("f", "n"):
                self.args[arg] = False
            else:
                # TODO make this error a template
                return f"invalid value {value} for boolean arg {arg}, use true/false"

        elif isinstance(self.args[arg], int):
            if value.isdigit():
                self.args[arg] = int(value)
            else:
                return f"invalid value {value} for integer arg {arg}, use an integer"

        return f"Successfully set {arg} to {self.args[arg]}"

    def profile(self):
        return utils.description(*[
            utils.description(*field, newlines=0)
            for field in [("name", self.name), ("id", self.get_id())] +
            self.stats.print_stats(self.inventory.modifers(), list_=True)
        ], mode="long")

    commands = {
        "rest": rest,
        "warp": warp,
        "set": set_,
        # TODO: flee command to leave a fight (penalty for fleeing?)
    }
    fight_commands = {
        "attack": attack,
        "heal": heal,
    }


class Party:
    """party of players"""
    def __init__(self, host, *players):
        self.host = host
        self.players = list(players) + [host]
        self.fighting = {}
        self.doing_stuff = None
        self.counter = 0
        self.action_queue = []

    def join(self, player):
        """adds a player to a party"""
        player.party = self
        self.players.append(player)

    def leave(self, player):
        """removes a player"""
        player.party = Party(player)
        self.players.remove(player)

    def kick(self, player_name):
        pass

    def killed_enemy(self, enemy, player):
        """changes stuff based on enemy"""
        text = ""
        text += f"{enemy.name} is now dead!\n"

        exp_earned = enemy.stats.level ** 2
        gold_earned = int(enemy.stats.max_health / 10) + random.randint(1, 10)

        text += f"You earned {exp_earned} exp and {gold_earned} gold!"
        player.stats.exp += exp_earned
        player.stats.balance += gold_earned
        del self.fighting[enemy.name]

        if not self.fighting:
            text += "enemies defeated (placeholder)"
            self.counter = 0

        return text

    def get_enemy(self):
        # TODO: let player pick enemy to attack
        return random.choice(list(self.fighting.values()))

    def fight(self, *args):
        output_text = ""
        if not self.fighting:
            output_text += self.start_fight()
        else:
            output_text += f"currently fighting {utils.join_items(*self.fighting, separator=', ')}"
        if not self.doing_stuff:
            self.next_turn()

        output_text += self.do_stuff()
        if not self.fighting:
            output_text += "enemies defeated (placeholder)"
            self.counter = 0
        return output_text

    def do_stuff(self):
        output_text = f"it is {self.doing_stuff}'s turn"
        if self.doing_stuff in self.fighting:
            output_text += self.fighting[self.doing_stuff].attack(
                random.choice(self.players)
            )
            self.doing_stuff = None
        return utils.newline(output_text)

    def next_turn(self):
        if not self.doing_stuff:
            while not self.action_queue:
                self.counter += 1
                for thing in self.players + list(self.fighting.values()):
                    if self.counter % thing.stats.speed == 0:
                        self.action_queue.append(thing.name)
            self.doing_stuff = self.action_queue.pop()

    def start_fight(self):
        # get enemies from room
        enemy = classes.rooms[self.host.room].generate_enemy()
        self.fighting[enemy.name] = enemy
        self.next_turn()

        return utils.description(
            f"{enemy.name} has approached to fight!",
            *[
                utils.description(*field)
                for field in enemy.stats.print_stats(list_=True)
            ], mode="long"
        )

    commands = {
        "join": join,
        "leave": leave,
        "kick": kick
    }


players = {}
parties = {}
