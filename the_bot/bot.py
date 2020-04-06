"""
bot for hangouts
"""
import hangups
import asyncio
from handler import Handler
import utils
import sys
# import signal


class Bot:
    """bot for hangouts"""

    ignore = (
        105849946242372037157,  # odlebot
        11470746254329358783,  # saberbot
        104687919952293193271,  # Ether(chendibot)
    )

    def __init__(self):
        self.cookies = hangups.get_auth_stdin("./token.txt", True)
        self.client = hangups.Client(self.cookies)
        self.handler = Handler()
        self.output_text = ""

    def run(self):
        """main loop for running bot"""
        self.client.on_connect.add_observer(self._on_connect)
        # self.client.on_disconnect.add_observer(self._on_disconnect)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())
        sys.exit(0)

    async def _on_connect(self):
        """called when bot connects to hangouts"""
        self._user_list, self._convo_list = (await hangups.build_user_conversation_list(self.client))
        self._convo_list.on_event.add_observer(self._on_event)
        print("Connected!")

    async def _on_event(self, event):
        """called when there is an event in hangouts"""
        user, conv = utils.getUserConv(self, event)
        # userID = user.id_[0]
        self.output_text = ""

        # handles messages
        if isinstance(event, hangups.ChatMessageEvent) and not user.is_self and not utils.userIn(self.ignore, user):
            commands = utils.command_parser(event.text)
            command = next(self.commands)

            if command in self.handler.keywords:
                self.output_text = self.handler.keywords[command]

            elif command in self.handler.images:
                if utils.cooldown(self.handler.cooldowns, user, event, 5):
                    return
                with open(f"{self.handler.images_folder}{self.handler.images[command]}", "rb") as image:
                    await conv.send_message(utils.toSeg(""), image)

            elif command in self.handler.commands:
                function_ = self.handler.commands[command]

            elif command in self.handler.games:
                function_ = self.handler.play_game

            if function_ and not utils.cooldown(self.handler.cooldowns, user, event, function_.cooldown_time):
                user, conv = utils.getUserConv(self, event)
                await function_(self, user, conv, commands)

        # new member
        elif isinstance(event, hangups.MembershipChangeEvent):
            if conv.get_user(event.participant_ids[0]).is_self and event.type_ == 1:
                self.output_text = "Saber in!"

        # sends message to hangouts
        if self.output_text:
            await conv.send_message(utils.toSeg(self.output_text))
