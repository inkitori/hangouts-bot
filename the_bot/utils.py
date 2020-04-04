import hangups
import decimal  # why is this here
import json


def toSeg(text):
    return hangups.ChatMessageSegment.from_str(text)


def getUserConv(bot, event):
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)

    return user, conv


def cooldown(cooldowns, user, event, cooldown):
    text = event.text.lower()
    strippedTime = event.timestamp.replace(tzinfo=None)

    if user in cooldowns and text.split()[0] in cooldowns[user]:
        if (strippedTime - cooldowns[user][text.split()[0]]).seconds < cooldown:
            return cooldown - (strippedTime - cooldowns[user][text.split()[0]]).seconds
        else:
            cooldowns[user][text.split()[0]] = strippedTime
    else:
        cooldowns[user][text.split()[0]] = strippedTime


def isIn(userList, user):
    if int(user.id_[0]) in userList:
        return True


def scientific(number):
    return "{:.2e}".format(number)


def save(file_name, contents):
    with open(file_name, "w") as f:
        json.dump(contents, f, indent=4)


def load(file_name):
    with open(file_name, "r") as f:
        return json.load(file_name)


def newline(text, number=1):
    """adds number newlines to the end of text"""
    return text.strip() + ("\n" * number)


def get_item_safe(sequence, indexes=(0), defaults=("")):
    """
    Retrives the items at the indexes in sequence
    defaults to default if the item des not exist
    """
    items = []
    if len(defaults) == 1:
        defaults = defaults * len(indexes)
    for index, default in zip(indexes, defaults):
        try:
            item = sequence[index]
        except IndexError:
            item = default
        items.append(item)
    return items


def clean(text, split=True):
    """cleans user input and returns as a list"""
    if text:
        if type(text) == str:
            text = text.strip().lower()
            if split:
                text = text.split(' ')
            return text
        elif type(text) == list:
            return text
    else:
        return [""]


def trim(text, number=1, default=[""]):
    """
    trims the front of a sequence by number
    returns default if number is greater than len(sequence)
    """
    if type(text) == str:
        text = clean(text)
    if type(text) == list:
        for i in range(number):
            try:
                text = text[number:]
            except IndexError:
                text = default
                break
        return text
    else:
        return["something is wrong"]


def get_key(dictionary, item, *ignore):
    dictionary = dictionary.copy()
    for key in ignore:
        try:
            del dictionary[key]
        except KeyError:
            pass
    key_index = list(dictionary.values()).index(item)
    return list(dictionary.keys())[key_index]
