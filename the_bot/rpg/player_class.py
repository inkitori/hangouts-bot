import math
import random
import string

import game_utils
import rpg.classes as classes
import rpg.inventory_class as inventory_class
import utils


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
        self.options = {
            "autofight": False, "auto_join_party": True
        }
        self.inventory = inventory_class.Inventory()
        self.party_name = self.name
        Party(self.name)

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
        rooms = classes.rooms
        room = next(commands)
        party = parties[self.party_name]

        if not room:
            return "Invalid argument! use warp {room}"
        elif party.fighting:
            return "You can't warp while in a fight!"

        elif self.name != party.host_name:
            return "only the host of a party can warp"

        elif room not in rooms:
            return "That room doesn't exist!"

        elif room == self.room:
            return "You are already in that room!"

        self.room = room
        return "Successfully warped!"

    def rest(self, commands):
        """rests player"""
        if classes.rooms[self.room].can_rest:
            self.stats.health = "full"
            self.stats.mana = "full"
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

        self.stats.mana -= tome.stats.mana
        self.stats.health += tome.stats.health

        return utils.newline(f"You have been healed back up to {self.stats.health}")

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
            text += parties[self.party_name].killed_enemy(enemy, self)

        elif self.stats.health <= 0:
            text += self.party_name.died(enemy, self)

        return text

    def fight_action(self, action, commands):
        """"""
        party = parties[self.party_name]
        if not party.fighting and action is Player.attack:
            if self.name != party.host_name:
                return "you are not in a fight. Only hosts may start fights"
            else:
                return party.fight(commands)
        if self.name != party.doing_stuff:
            party.fight()
            return f"it is {party.doing_stuff}'s turn (not urs)" 
        output_text = action(self, commands, party.get_enemy())
        party.doing_stuff = None
        if party.fighting:
            party.fight()

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
        error_template = string.Template("invalid value $value for $type arg $arg, use $valid")

        # input validation
        if arg not in self.options:
            return "That is not a valid arg!"
        elif not arg:
            return "you must provide an arg"
        elif not value:
            return "you must provide a value"

        if isinstance(self.options[arg], bool):
            if value.startswith("t"):
                self.options[arg] = True

            elif value.startswith("f"):
                self.options[arg] = False
            else:
                return error_template.substitute(value=value, type="bool", arg=arg, valid="t/f")

        elif isinstance(self.options[arg], int):
            if value.isdigit():
                self.options[arg] = int(value)
            else:
                return error_template.substitute(
                    value=value, type="integer", arg=arg, valid="a whole number"
                )

        return f"Successfully set {arg} to {self.options[arg]}"

    def profile(self):
        return utils.description(*[
            utils.description(*field, newlines=0)
            for field in [("name", self.name), ("id", self.get_id())] +
            self.stats.print_stats(self.inventory.modifers(), list_=True)
        ], mode="long")

    def join(self, commands=utils.command_parser(""), has_permission=False, party_name=""):
        """adds player to a party"""
        output_text = ""
        party_name = utils.default(party_name, next(commands))
        if not party_name:
            return "you must provide a party name"
        elif party_name == self.party_name:
            return "you are already in that party"
        party = parties.get(party_name, None)
        if party is None:
            return "that party does not exist"

        host = game_utils.get_players(players, party.host_name, single=True)
        if host.options["auto_join_party"] or has_permission:
            output_text += self.leave(self.party_name, joining=True)
            if not output_text.startswith("left"):
                return output_text
            self.party_name = party_name
            output_text += (
                f"joined party {self.party_name} with players"
                f" {utils.join_items(*party.all_players(), separator=', ')}"
            )
            party.player_names.append(self.name)
        else:
            output_text += utils.join_items(
                f"party host {host.name} has auto join set to false,",
                "so you need to await approval to join.",
                "Your request has been added to the party requests list",
                separator=" "
            )
            party.join_requests.append(self.name)
        return output_text

    def leave(self, commands, joining=False):
        """removes a player"""
        party = parties[self.party_name]
        if party.host_name == self.name:
            if party:
                return "hosts cannot leave their party while their party has other members"
            elif not joining:
                return "theres no one but you, why would you leave?"
        else:
            party.player_names.remove(self.name)
        if not party:
            del parties[self.name]
        if not joining:
            self.party_name = Party(self.name).name()
        return utils.newline(f"left party")

    def accept(self, commands):
        player_name = next(commands)
        if not player_name:
            return "you must provide a player name"
        party = parties[self.party_name]
        if party.host_name != self.name:
            return "only hosts can accept join requests"
        elif player_name not in party.join_requests:
            return "that player has not requested to join"

        party.join_requests.remove(player_name)
        return utils.newline(
            game_utils.get_players(players, player_name, single=True).join(
                party_name=self.party_name, has_permission=True
            )
        )

    def decline(self, commands):
        player_name = next(commands)
        if not player_name:
            return "you must provide a player name"
        party = parties[self.party_name]
        if party.host_name != self.name:
            return "only hosts can decline join requests"
        elif player_name not in party.join_requests:
            return "that player has not requested to join"

        party.join_requests.remove(player_name)
        return f"{player_name} has been declined from joining the party"

    def kick(self, commands):
        kick_name = next(commands)
        if not kick_name:
            return "you must specify a player to kick"
        party = parties[self.party_name]
        if party.host_name != self.name:
            return "You must be the host to kick"
        for player_name in party.player_names:
            if kick_name == player_name:
                game_utils.get_players(
                    players, player_name, single=True
                ).leave(commands)
                return f"{kick_name} has been kicked from your party"

        return "no users in your party go by that name"

    def parties(self, commands):
        return utils.join_items(
            *[
                [party_name] + party.all_players()
                for party_name, party in parties.items()
            ],
            description_mode="long",
        )

    commands = {
        "rest": rest,
        "warp": warp,
        "set": set_,
    }
    fight_commands = {
        "attack": attack,
        "heal": heal,
    }
    """
    removed due to obnoxious bugs which were not worth fixing
    party_commands = {
        "join": join,
        "leave": leave,
        "kick": kick,
        "parties": parties,
        "accept": accept,
        "decline": decline
    }
    """


class Party:
    """party of players"""

    def __init__(self, host_name, *player_names):
        parties[host_name] = self
        self.host_name = host_name
        self.player_names = list(player_names)
        self.fighting = {}
        self.doing_stuff = None
        self.counter = 0
        self.action_queue = []
        self.join_requests = []

    def name(self):
        return utils.get_key(parties, self)

    def all_players(self):
        return self.player_names + [self.host_name]

    def __bool__(self):
        return bool(self.player_names)

    def killed_enemy(self, enemy, player):
        """changes stuff based on enemy"""
        text = ""
        text += f"{enemy.name} is now dead!\n"

        exp_earned = enemy.stats.level ** 2
        gold_earned = int(enemy.stats.max_health / 10) + random.randint(1, 10)

        text += utils.newline(
            f"You earned {exp_earned} exp and {gold_earned} gold!")
        player.stats.exp += exp_earned
        player.stats.balance += gold_earned
        del self.fighting[enemy.name]

        if not self.fighting:
            text += "enemies defeated"
            self.fighting = {}
            self.counter = 0

        return text

    def get_enemy(self):
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
            output_text += "enemies defeated!"
            self.counter = 0
        return output_text

    def do_stuff(self):
        output_text = f"it is {self.doing_stuff}'s turn"
        if self.doing_stuff in self.fighting:
            output_text += self.fighting[self.doing_stuff].attack(
                random.choice([
                    player for player in players.values()
                    if player.name in self.all_players()
                ])
            )
            self.doing_stuff = None
        return utils.newline(output_text)

    def next_turn(self):
        if not self.doing_stuff:
            while not self.action_queue:
                self.counter += 1
                for name in self.all_players() + list(self.fighting):
                    if name in self.fighting:
                        speed = self.fighting[name].stats.speed
                    elif name in self.all_players():
                        speed = game_utils.get_players(
                            players, name, single=True).stats.speed
                    if self.counter % speed == 0:
                        self.action_queue.append(name)
                random.shuffle(self.action_queue)
            self.doing_stuff = self.action_queue.pop()

    def start_fight(self):
        # get enemies from room
        enemy = classes.rooms[
            game_utils.get_players(
                players, self.host_name, single=True).room
        ].generate_enemy()
        self.fighting[enemy.name] = enemy
        self.next_turn()

        return utils.description(
            f"{enemy.name} has approached to fight!",
            *[
                utils.description(*field)
                for field in enemy.stats.print_stats(list_=True)
            ], mode="long"
        )


players = {}
parties = {}
