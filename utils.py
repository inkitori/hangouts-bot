import hangups


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
