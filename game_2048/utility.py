"""
ramdom useful functions
"""


def newline(text, number=1):
    """adds number newlines to the end of text"""
    return text.strip() + ("\n" * number)


def get_item_safe(sequence, index=0, default=""):
    """
    Retrives the item at index in sequence
    defaults to default if the item des not exist
    """
    try:
        item = sequence[index]
    except IndexError:
        item = default
    return item


def clean(text):
    """cleans user input and returns as a list"""
    if text:
        if type(text) == str:
            return text.strip().lower().split()
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
