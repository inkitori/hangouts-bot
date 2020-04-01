import hangups
from hangups.ui.utils import get_conv_name
import asyncio
from handler import Handler
from utils import *
import sys

import signal


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
        convs = self._convo_list.get_all()
        print("Connected!")

    async def _on_disconnect(self):
        print("ded")

    async def _on_event(self, event):
        user, conv = getUserConv(self, event)
        userID = user.id_[0]
        userData = self.handler.data["users"]

        if isinstance(event, hangups.ChatMessageEvent) and (not user.is_self):
            if userID in userData and event.text.strip().lower() != "/prestige_confirm":
                userData[userID]["prestige_confirm"] = 0

            strippedText = event.text.strip().lower()

            if strippedText in self.handler.keywords:
                await conv.send_message(toSeg(self.handler.keywords[strippedText]))

            elif strippedText.split()[0] in self.handler.images:
                if cooldown(self.handler.cooldowns, user, event, 5):
                    return
                f = open(self.handler.images[strippedText.split()[0]], "rb")
                await conv.send_message(toSeg(""), f)
                f.close()

            elif strippedText.split()[0] in self.handler.commands:
                await self.handler.commands[strippedText.split()[0]](self, event)

        elif isinstance(event, hangups.MembershipChangeEvent):
            if conv.get_user(event.participant_ids[0]).is_self and event.type_ == 1:
                await conv.send_message(toSeg("Saber in!"))


bot = Bot()
bot.run()
