"""
functions shared between games that don't fit in utils
"""
import utils


def profile(players, player, commands):
    """returns player profiles"""
    output_text = ""
    player_name = commands.send("remaining")

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

    output_text += utils.join_items(
        *[
            player.profile()
            for player in possible_players
        ], end="\n"
    )
    return output_text
