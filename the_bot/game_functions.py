"""
functions shared between games that don't fit in utils
"""
import utils
import math

hangouts_char_limit = 2000


def profile(self, player, commands):
    """returns player profiles"""
    players = self.players
    output_text = ""
    player_name = next(commands)
    page = utils.default(next(commands), 1)

    # create list of players
    possible_players = []
    for possible_player in players.values():
        if player_name in possible_player.name:
            possible_players.append(possible_player)
    if player_name.isdigit() and int(player_name) in players:
        possible_players.append(players[int(player_name)])
    elif player_name == "self":
        possible_players.append(player)

    # input validation
    if not possible_players:
        return "No players go by that name/id!"

    elif len(possible_players) > 1:
        output_text += utils.newline(
            f"{len(possible_players)} player(s) go by that name:")
    try:
        possible_players_slice = possible_players[(
            page - 1) * 5: ((page - 1) * 5) + 4]
    except IndexError:
        if page * 5 > len(possible_players):
            possible_players_slice = possible_players[0:]
        else:
            possible_players_slice = possible_players[(page - 1) * 5:]

    output_text += utils.join_items(
        *[
            player.profile()
            for player in possible_players_slice
        ], separator="\n" * 2
    ) + f"{page}/{math.ceil(len(possible_players)/5)}"
    return output_text


def get_possible_players(players, player_name, running_player=None):
    possible_players = []
    for possible_player in players.values():
        if player_name in possible_player.name:
            possible_players.append(possible_player)
    if player_name.isdigit() and int(player_name) in players:
        possible_players.append(players[int(player_name)])
    elif player_name == "self" and running_player:
        possible_players.append(running_player)
