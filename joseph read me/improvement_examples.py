"""
examples of improving and cleaning code for joseph
in reverse chronological order (newest on top)
"""
# i wrote functions to deal with this nonsense
# also, variables exist for a reason
# u are goining about cleaning ur input wrong. the input sohuld be cleaned once, by rpg process
# ur making every function clean it's unput, which in ineffecient
def rpg_process(self, userID, event_text):
    # although clean protects you from an empty list
    # it doesnt create a second item
    # ur playing with fire here
    # that is why i made a function for it
    command = clean(event_text)[1]
    # what is this? if u want the full command, then save the list
    # then get items as needed
    full_command = clean(event_text, 1)[1]
    # this is fine
    if command not in self.commands:
        return "That command doesn't exist!"
    # register should handle this, not rpg_process
    # ur mixing differnet levels of abstraction
    # VERY BAD
    elif command == "register" and userID in self.userData:
        return "You are already registered!"

    # this is fine, it makes sense for rpg_process to do user validation
    elif command != "register" and userID not in self.userData:
        return "You are not registered! Use /register"
    # this is also fine, but u dont need to put it in else cause u used return
    else:
        self.commands[command](userID, full_command)
def warp(self, userID, command):
    # rooms in only used once,its not rally worth the variable
    rooms = self.data["rooms"]
    users = self.userData
    if len(command.split()) != 2:
        return "Invalid arguments! /warp {room}"

    elif self.userData[userID]["fighting"]:
        return "You can't warp while in a fight!"

    elif command.split()[1] not in rooms:
        return "That room doesn't exist!"

    elif rooms[command.split()[1]]["required_lvl"] > users[userID]["lvl"]:
        return "Your level is not high enough to warp there!"

    elif command.split()[1] == users[userID]["room"]:
        return "You are already in that room!"
    else:
        users[userID]["room"] = command.split()[1]
        save("data.json", self.data)
        return "Successfully warped!"
#######
def rpg_process(self, userID, event_text):
    # replaced full_command with commands, cause ur gonna cut up comands anyway
    commands = clean(event_text)
    # u dont need the /rpg prefix, so cut it off
    commands = trim(commands)
    # this protects u from errors while retrieving
    command = get_item_safe[commands]
    if not command:
        # u might want to replace this with basic help text
        # or the curent state of the game, incase they forgot
        # eg. "u r in the village, enter help for help"
        return "you must enter a command"


    elif command not in self.commands:
        return "That command doesn't exist!"

    # because it requires that the user call register
    # the register function should handle this
    # therefore, move it to the register function
    #if userID in self.userData:
    #    return "You are already registered!"

    elif command != "register" and userID not in self.userData:
        return "You are not registered! Use /register"
    # command should currently be set to the command we need to call
    # so we can cut it out of the commands list now
    commands = trim(commands)
    self.commands[command](userID, commands)


# use this as an example of how to use the utils function i wrote
# remember that the input is the cleaned commands (a list)
# we already cut off "/rpg" and "warp" in rpg_process
# so the next word should be the room
def warp(self, userID, command):
    rooms = self.data["rooms"]
    users = self.userData
    room = get_item_safe(commands)
    if not room:
        return "Invalid argument! use warp {room}"
    # this needs updating, but i haven't written the user class yet
    if self.userData[userID]["fighting"]:
        return "You can't warp while in a fight!"

    elif room not in rooms:
        return "That room doesn't exist!"

    elif rooms[room]["required_lvl"] > users[userID]["lvl"]:
        return "Your level is not high enough to warp there!"

    elif room == users[userID]["room"]:
        return "You are already in that room!"
    else:
        users[userID]["room"] = room
        save("data.json", self.data)
        return "Successfully warped!"



# ur returning a boolean based on expression which evaluates to a bool
# the redundancy is obvious
def userIn(userList, user):
    if int(user.id_[0]) in userList:
        return True
########
def userIn(userList, user):
    return int(user.id_[0]) in userList
# this code is clearly tailored for user lists, so make it obvious
# be clear about what everything does
#######
def userIn(userList, user):
    return int(user.id_[0]) in userList



# what is this? its repetitive. also, i made functions to deal with this in utils
userID = command.split()[1]
key = command.split()[2]
value = command.split(' ', 3)[3]
#########
# clean lowers, strips, then splits and also deals with empty strings so u dont get an empty list
command_list = utils.clean(commands)
# this handles index errors for u and is much shorter
userID, key, value = get_item_safe(command_list, (1, 2, 3))



# this one should be obvious
if random.randint(0, 1):
    damage_dealt += math.sqrt(damage_dealt/2)
else:
    damage_dealt -= math.sqrt(damage_dealt/2)
#########
multiplier = random.choice((1, -1))
damage_taken += multiplier * math.sqrt(damage_dealt / 2)
