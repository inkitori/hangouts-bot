import hangups
import asyncio
import random
from text_2048 import play_game

class Handler:
    def __init__(self):
        self.keywords = {
                "good bot": "nyaa, thanku~~",
                "bad bot": "nuu dun pweese~~ >.<",
                "headpat": "uwu thanku",
                "yamete": "kudasai!~~",
                "ping": "pong"
        }
        self.commands = {
                "/help": self.help,
                "/rename": self.rename,
                "/say": self.say,
                "/rickroll": self.rickroll,
                "/quit": self.quit
        }
        self.images = {
                "/gay": "images/gay.jpg",
                "/math": "images/math.jpg",
                "/praise": "images/praise.jpg",
                "/goddammit": "images/goddammit.jpg",
                #"/heymister": "images/heymister.png"
            }
        self.admins = [] # fill in yourself

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str(event.text.split(' ', 1)[1]))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /say {message}"))

    async def rickroll(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Something went wrong!"))

    async def quit(self, bot, event):
        user, conv = getUserConv(bot, event)
        print(type(str(user.emails).strip().lower()[2:-2]))

        try:
            if str(user.emails).strip().lower()[2:-2] in self.admins:
                await conv.send_message(hangups.ChatMessageSegment.from_str("Saber out!"))
                await bot.client.disconnect()
            else:
                await conv.send_message(hangups.ChatMessageSegment.from_str("bro wtf u can't use that"))
        except:
                await conv.send_message(hangups.ChatMessageSegment.from_str("Something went wrong!"))

    async def help(self, bot, event):
        user, conv = getUserConv(bot, event)

        help_text = "**Keywords:**\n"
        for x in self.keywords:
            help_text += x + '\n'

        help_text += "\n**Commands:**\n"
        for x in self.commands:
            help_text += x + '\n'
        for x in self.images:
            help_text += x + '\n'

        help_text += "\nI'm a bot by Yeah. You can view my source at https://github.com/YellowPapaya/hangouts-bot"
        await conv.send_message(hangups.ChatMessageSegment.from_str(help_text))

def getUserConv(bot, event):
    conv = bot._convo_list.get(event.conversation_id)
    user = conv.get_user(event.user_id)

    return user, conv
