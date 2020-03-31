import hangups

def toSeg(text):
    return hangups.ChatMessageSegment.from_str(text)

def getUserConv(bot, event):
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)

    return user, conv

