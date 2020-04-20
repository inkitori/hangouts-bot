"""
assorted useful functions
"""
import hangups
import json
import inspect
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# hangouts
def toSeg(text):
    """converts string to hangouts message"""
    return hangups.ChatMessageSegment.from_str(text)


def get_user_and_conv(bot, event):
    """gets user and conversation from a hangouts event"""
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)
    return user, conv


def cooldown(cooldowns, user, event, cooldown):
    """checks cooldown for a command and user"""
    text = clean(event.text)
    command = get_item(text)
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
    """checks if the user is in user_list"""
    return int(user.id_[0]) in user_list


# formatting
def scientific(number):
    """returns a string in scientific number format"""
    return "{:.2e}".format(number)


def join_items(*items, seperator="\n", is_description=False, description_mode="short", end="\n"):
    """
    joins a list using seperator
    if is_description, passes each item to description before joining
    """

    output_list = []
    if is_description:
        for item in items:
            output_list.append(description(*(item if item else ""), mode=description_mode))

    else:
        output_list = convert_items(list(items), type_=str)
    output_text = seperator.join(output_list).strip()
    output_text += end if not output_text.endswith(end) else ""
    return output_text


def newline(text, number=1):
    """returns text with esactly number newlines at the end"""
    return text.strip() + ("\n" * number)


def description(name, *description, mode="short", end="\n"):
    """
    chendis stupid string formatting function

    short - formats, like, this
    long:
        formats
        like
        this
    """
    # prevents errors
    description = convert_items(list(description), str)

    if mode == "short":
        description = join_items(*description, seperator=", ")
        full_description = f"{name} - {description}"
    if mode == "long":
        description.insert(0, f"{name.title()}:")
        full_description = join_items(*description, seperator="\n\t", end=end)
    return full_description.strip()


# json
def save(file_name, contents):
    """saves data into a json"""
    with open(file_name, "w") as file:
        json.dump(contents, file, indent=4)


def load(file_name):
    """loads a dict from a json"""
    with open(file_name, "r") as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            print("could not load data")


# processing strings
def clean(text, split=True):
    """cleans user input and returns as a list"""
    if text:
        if isinstance(text, str):
            text = text.strip().lower()
            if split:
                text = text.split()
            return text
    else:
        return [""]


def trim(text, number=1, default=[""]):
    """
    removes the first number items from a sequence
    returns default if number is greater than len(sequence)
    """
    try:
        text = text[number:]
    except IndexError:
        text = default
    return text


def command_parser(command_text):
    """
    returns a generator of commands
    retunrs empty string if there are no more commands
    """
    commands = clean(command_text)
    current_index = 0
    val = None
    while True:
        if isinstance(val, int):
            current_index += val
            current_index = clamp(current_index, 0, len(commands))
            item = None
        elif val == "remaining":
            item = join_items(*commands[current_index:], seperator=" ", end="")
        else:
            item = get_item(commands, indexes=(current_index, ))
            current_index += 1
        val = yield item


# get things without errors
def get_item(sequence, indexes=(0, ), default=""):
    """
    Retrives the items at the indexes in sequence
    defaults to default if the item does not exist
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


def get_key(dictionary, item, *ignore):
    """
    gets a key using a value
    assumes unique values
    ignores keys in ignore
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
    """
    gets the value of a key from a dictionary
    returns default if the key does not exist
    """
    try:
        value = dictionary[key]
    except KeyError:
        value = default
    return value


# random
def clamp(value, min_value, max_value):
    """makes value less than max and greater than min"""
    return max(min_value, min(value, max_value))


def is_yes(text):
    """
    checks if text starts with y
    because i am a lazy bum
    """
    return get_item(clean(text, split=False)) == "y"


def convert_items(items, type_, default=""):
    """converts items to type or replaces with default"""
    for i in range(len(items)):
        try:
            items[i] = type_(items[i])
        except ValueError:
            items[i] = default
    return items


# google api
def create_sheets_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # delete token.pickle if changing scopes
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("sheets", "v4", credentials=creds)


def get_named_ranges(sheets, spreadsheetID, sheet_name="Sheet1", included="all"):
    """gets all the named ranges from a spreadsheet and converts to a1 notation"""
    sheet_data = sheets.get(spreadsheetId=spreadsheetID).execute()
    named_ranges = sheet_data["namedRanges"]
    named_ranges_dict = {}
    for named_range in named_ranges:
        range_name = named_range["name"]
        if range_name in included or included == "all":
            range_notation = a1_notation(*[
                named_range["range"][i]
                for i in ["startRowIndex", "endRowIndex", "startColumnIndex", "endColumnIndex"]
            ])
            named_ranges_dict[range_name] = f"{sheet_name}!{range_notation}"

    return named_ranges_dict


def a1_notation(first_row, last_row, first_column, last_column):
    start = f"{num_to_col_letters(first_column + 1)}{first_row + 1}"
    end = f"{num_to_col_letters(last_column)}{last_row}"
    return f"{start}:{end}"


def num_to_col_letters(num):
    letters = ""
    while num:
        mod = (num - 1) % 26
        letters += chr(mod + 65)
        num = (num - 1) // 26
    return "".join(reversed(letters))
