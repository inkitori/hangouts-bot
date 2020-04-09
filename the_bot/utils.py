"""
assorted useful functions
"""
import hangups
import json
import inspect


def toSeg(text):
    """converts string to hangouts message"""
    return hangups.ChatMessageSegment.from_str(text)


def getUserConv(bot, event):
    """gets user and conversation"""
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)

    return user, conv


def cooldown(cooldowns, user, event, cooldown):
    """checks cooldown for a command and user"""
    text = clean(event.text)
    command = get_item_safe(text)
    stripped_time = event.timestamp.replace(tzinfo=None)
    cooldown_time = cooldowns[user][command]

    if user in cooldowns and command in cooldowns[user]:
        if (stripped_time - cooldown_time).seconds < cooldown:
            return cooldown - (stripped_time - cooldown_time).seconds
        else:
            cooldown_time = stripped_time
    else:
        cooldown_time = stripped_time
    cooldowns[user][command] = cooldown_time


def userIn(user_list, user):
    """checks if the user is in user_List"""
    return int(user.id_[0]) in user_list


def scientific(number):
    """returns a string in scientific number format"""
    return "{:.2e}".format(number)


def save(file_name, contents):
    """saves data into a json"""
    with open(file_name, "w") as file:
        json.dump(contents, file, indent=4)


def load(file_name):
    """loads a file from a json"""
    with open(file_name, "r") as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            return "could not load data"


def join_items(*list, seperator="\n"):
    """joins a list using seperator"""
    return seperator.join(list)


def newline(text, number=1):
    """adds number newlines to the end of text"""
    return text.strip() + ("\n" * number)


def get_item_safe(sequence, indexes=(0,), default=""):
    """
    Retrives the items at the indexes in sequence
    defaults to default if the item des not exist
    """
    if inspect.isgenerator(sequence):
        return next(sequence)
    items = []
    for index in indexes:
        try:
            item = sequence[index]
        except IndexError:
            item = default
        if len(indexes) == 1:
            items = item
        else:
            items.append(item)
    return items


def clean(text, split=True):
    """cleans user input and returns as a list"""
    if text:
        if isinstance(text, str):
            text = text.strip().lower()
            if split:
                text = text.split(' ')
            return text
        elif isinstance(text, list):
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


def command_parser(command_text, has_prefix=False):
    """returns a generator of commands"""
    commands = clean(command_text)
    if has_prefix:
        commands = trim(commands)
    while True:
        yield get_item_safe(commands)
        commands = trim(commands)


def get_key(dictionary, item, *ignore):
    """
    gets a key using a value
    assumes unique values
    will ignore keys in ignore
    """
    dictionary = dictionary.copy()
    for key in ignore:
        try:
            del dictionary[key]
        except KeyError:
            pass
    key_index = list(dictionary.values()).index(item)
    return list(dictionary.keys())[key_index]


def get_value(dictionary, key, default=""):
    """safely gets the value of a key from a dictionary"""
    try:
        value = dictionary[key]
    except KeyError:
        value = default
    return value


def clamp(value, min, max):
    """clamps value inside min and max"""
    if value < min:
        value = min
    elif value > max:
        value = max
    return value


def is_yes(text):
    """checks if a text input starts with y"""
    return get_item_safe(clean(text, split=False)) == "y"


def description(name, *description):
    if len(description) == 1:
        full_description = f"{name} - {description[0]}"
    else:
        description = join_items(*description, seperator="\n\t")
        full_description = f"{name.title()}:\n{description}"
    return full_description
