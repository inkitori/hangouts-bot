import hangups
from hangups import hangouts_pb2 
from hangups.hangouts_pb2 import ParticipantId

import asyncio
import random
from collections import defaultdict
from datetime import datetime, tzinfo

from utils import *
#from text_2048 import play_game

class Handler:
    def __init__(self):
        self.keywords = {
                "good bot": "nyaa, thanku~~",
                "bad bot": "nuu dun pweese~~ >.<",
                "headpat": "uwu thanku",
                "yamete": "kudasai!~~",
                "ping": "pong",
                "pong": "ping",
                "saber": "hi"
        }
        self.commands = {
                "/help": self.help,
                "/rename": self.rename,
                "/say": self.say,
                "/rickroll": self.rickroll,
                "/quit": self.quit,
                "/reset": self.reset,
                "/id": self.id,
                "/kick": self.kick
        }
        self.images = {
                "/gay": "images/gay.jpg",
                "/math": "images/math.jpg",
                "/praise": "images/praise.jpg",
                "/goddammit": "images/goddammit.jpg",
                "/heymister": "images/heymister.png"
            }
        self.users = defaultdict(dict) 
        self.admins = [] # fill in yourself (store as int)

    # utility
    async def help(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 10):
            return

        f = open("help.txt", 'r')
        contents = f.read()
        await conv.send_message(toSeg(contents))
        f.close()

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 3):
            return
        
        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except:
            await conv.send_message(toSeg("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 3):
            return

        try:
           await conv.send_message(toSeg(event.text.split(' ', 1)[1]))
        except:
            await conv.send_message(toSeg("Format: /say {message}"))
    async def id(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 10):
            return

        try:
            await conv.send_message(toSeg(user.id_[0]))
        except:
            await conv.send_message(toSeg(str("Something went wrong!")))

    async def kick(self, bot, event):
        user, conv = getUserConv(bot, event)
        arg1 = event.text.lower().split()[1]
        users = conv.users
        ids = []
        kick_users = []

        #try:
        for user in users:
            if arg1 in user.full_name.lower():
                kick_users.append(user)

        if not kick_users:
            await conv.send_message(toSeg("Nobody in this conversation goes by that name"))
            return
        # only reason i figured this out was because of hangupsbot, so thank you so much https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

        ids = [ParticipantId(gaia_id = user.id_.gaia_id, chat_id = conv.id_) for user in kick_users]

        for kick_id in ids:
            request = hangouts_pb2.RemoveUserRequest(request_header = bot.client.get_request_header(), participant_id = kick_id, event_request_header = conv._get_event_request_header())
            res = await bot.client.remove_user(request)
            conv.add_event(res.created_event)
        #except:
            #await conv.send_message(toSeg("Yeah don't use this command lol"))

    # fun
    async def rickroll(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 3):
            return

        try:
            await conv.send_message(toSeg("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

    # config 
    async def quit(self, bot, event):
        user, conv = getUserConv(bot, event)
        if self.cooldown(user, event, 30):
            return

        try:
            if self.isAdmin(user):
                await conv.send_message(toSeg("Saber out!"))
                await bot.client.disconnect()
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
                await conv.send_message(toSeg("Something went wrong!"))

    async def reset(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            arg1 = '/' + event.text.lower().split()[1]
            if self.isAdmin(user):
                if arg1 in self.users[user]:
                    self.users[user][arg1] = datetime.min.replace(tzinfo=None)
                else:
                    await conv.send_message(toSeg("Format: /reset {command}"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Format: /reset {command}"))

    # helpers
    def cooldown(self, user, event, cooldown):
        text = event.text.lower()
        strippedTime = event.timestamp.replace(tzinfo=None)

        if user in self.users and text.split()[0] in self.users[user]:
            if (strippedTime - self.users[user][text.split()[0]]).seconds < cooldown:
                print(cooldown - (strippedTime - self.users[user][text.split()[0]]).seconds)
                return 1
            else:
                self.users[user][text.split()[0]] = strippedTime 
        else:
            self.users[user][text.split()[0]] = strippedTime

    def isAdmin(self, user):
        print(type(user.id_[0]))
        if int(user.id_[0]) in self.admins:
            return True
