"""
assorted useful functions
"""
import hangups
import shelve
import inspect
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# hangouts
def to_seg(text):
    """converts string to hangouts message"""
    return hangups.ChatMessageSegment.from_str(text)


def get_user_and_conv(conversations, event):
    """gets user and conversation from a hangups event"""
    conv = conversations.get(event.conversation_id)
    user = conv.get_user(event.user_id)
    return user, conv


def cooldown(cooldowns, user, event, cooldown):
    """checks cooldown for a command and user"""
    # TODO: either delete (this is unused) or clean up
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


def user_in(user_list, user):
    """
    checks if the user is in user_list, intended for hanugps useres

    Args:
        user_list - list of users to check against
        user - the user to check

    Returns bool
    """
    return int(user.id_[0]) in user_list


# formatting
def scientific(number):
    """returns a string in scientific number format"""
    return "{:.2e}".format(number)


def join_items(*items, separator="\n", description_mode=None, start="", end="", newlines=1):
    """
    joins items using separator, ending with end and newlines

    Args:
        *items - the things to join
        separator - what seperates items
        description_mode - what mode to use for description (defaults to no description)
        start - what to start the string with
        end - what to end the string with
        newlines - how many newlines to add after end (will remove all whitespace at end first)

    Returns a string
    """

    output_list = []
    if description_mode:
        for item in items:
            output_list.append(description(
                *(default(item, "")), mode=description_mode,
                newlines=0
            ))

    else:
        output_list = convert_items(list(items), type_=str)
    output_list = [item.strip() for item in output_list]
    output_text = separator.join(output_list).strip()
    output_text += default("", end, output_text.endswith(end))
    output_text = start + newline(output_text, newlines)
    return output_text


def newline(text, number=1):
    """returns text with esactly number newlines at the end"""
    return text.strip() + ("\n" * number)


def description(name, *description, mode="short", end="\n", newlines=1):
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
        description = join_items(*description, separator=", ", end=end, newlines=0)
        full_description = f"{name} - {description}"
    elif mode == "long":
        description.insert(0, f"{name.title()}:")
        full_description = join_items(*description, separator="\n\t", end=end, newlines=0)
    else:
        raise ValueError(f"mode {mode} does not exist for descriptions")
    return newline(full_description, newlines)


# save and load data
save_file_name = "save_data"


def save(**contents):
    """saves data into a file"""
    with shelve.open(save_file_name, writeback=True) as save_file:
        for name, data in contents.items():
            save_file[name] = data


def load(*names):
    """loads data from a file"""
    data = []
    with shelve.open(save_file_name) as save_file:
        for name in names:
            data.append(save_file[name])
    if len(data) == 1:
        data = data[0]
    return data


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
            item = get_item(commands, indexes=(current_index, ))
        elif val == "remaining":
            item = join_items(*commands[current_index:], separator=" ", newlines=0)
        elif val == "all":
            item = commands
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


def get_key(dictionary, item, *ignore, is_same=True):
    """
    gets a key using a value
    ignores keys in ignore
    """
    dictionary = dictionary.copy()
    for key in ignore:
        try:
            del dictionary[key]
        except KeyError:
            pass
    if is_same:
        key_index = list(dictionary.values()).index(item)
    else:
        for key, value in dictionary.items():
            if value == item:
                return key
        raise KeyError(item)
    return list(dictionary.keys())[key_index]


def get_value(dictionary, key, default=""):
    """
    gets the value of a key from a dictionary
    returns default if the key does not exist
    """
    # TODO: replace all calls with builtin dict.get(key, default)
    # TODO: then delete this function
    try:
        value = dictionary[key]
    except KeyError:
        value = default
    return value


def default(item, default=None, condition="no condition"):
    """returns default if not condition"""
    if condition == "no condition":
        condition = item
    return item if condition else default


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
def create_sheets_service(pickled_token_file="token.pickle"):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(pickled_token_file):
        with open(pickled_token_file, "rb") as token:
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
        with open(pickled_token_file, "wb") as token:
            pickle.dump(creds, token)

    return build("sheets", "v4", credentials=creds)


def get_named_ranges(sheets, spreadsheet_id, sheet_name="Sheet1", included="all"):
    """gets all the named ranges from a spreadsheet and converts to a1 notation"""
    sheet_data = sheets.get(spreadsheetId=spreadsheet_id).execute()
    named_ranges = sheet_data["namedRanges"]
    named_ranges_dict = {}
    for named_range in named_ranges:
        range_name = named_range["name"].lower()
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
