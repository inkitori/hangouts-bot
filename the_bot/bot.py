import hangups
from hangups.ui.utils import get_conv_name  # never used, y is it here
import asyncio
from rpg.rpghandler import RPGHandler
from handler import Handler
from utils import *
import sys

import signal  # u never use this y is it here


class Bot:
    def __init__(self):
        self.cookies = hangups.get_auth_stdin("./token.txt", True)
        self.client = hangups.Client(self.cookies)
        self.handler = Handler()

    def run(self):
        self.client.on_connect.add_observer(self._on_connect)
        self.client.on_disconnect.add_observer(self._on_disconnect)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())
        sys.exit(0)

    async def _on_connect(self):
        self._user_list, self._convo_list = (await hangups.build_user_conversation_list(self.client))
        self._convo_list.on_event.add_observer(self._on_event)
        print("Connected!")

    async def _on_disconnect(self):
        print("ded")

    async def _on_event(self, event):
        user, conv = getUserConv(self, event)
        userID = user.id_[0]
        userData = self.handler.data["users"]
        output_message = ""

        if isinstance(event, hangups.ChatMessageEvent) and not user.is_self:

            strippedText = clean(event.text)
            command = get_item_safe(strippedText)

            if command in self.handler.keywords:
                output_message = self.handler.keywords[command]

            elif command in self.handler.images:
                if cooldown(self.handler.cooldowns, user, event, 5):
                    return
                with open(self.handler.images_folder + self.handler.images[command], "rb") as image:
                    await conv.send_message(toSeg(""), image)

            elif command in self.handler.commands:
                await self.handler.commands[strippedText.split()[0]](self, event)

            elif command in self.handler.games:
                await self.handler.play_game(self, event)

        elif isinstance(event, hangups.MembershipChangeEvent):
            if conv.get_user(event.participant_ids[0]).is_self and event.type_ == 1:
                output_message = "Saber in!"
        if output_message:
            await conv.send_message(toSeg(output_message))

