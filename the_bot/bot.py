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
    """bot for hangouts (normal use case)"""

    ignore = (
        105849946242372037157,  # odlebot
        11470746254329358783,  # saberbot
        104687919952293193271,  # Ether(chendibot)
    )

    def __init__(self, options):
        self.cookies = hangups.get_auth_stdin(options.token, True)
        self.client = hangups.Client(self.cookies)
        self.handler = Handler()

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
        user, conv = utils.get_user_and_conv(self, event)
        output_text = ""

        # handles messages
        if isinstance(event, hangups.ChatMessageEvent) and not user.is_self and not utils.userIn(self.ignore, user):
            output_text = await self.handler.handle_message(event, bot=self)

        # new member
        elif isinstance(event, hangups.MembershipChangeEvent):
            if conv.get_user(event.participant_ids[0]).is_self and event.type_ == 1:
                output_text = "Saber in!"

        # sends message to hangouts
        if output_text:
            await conv.send_message(utils.toSeg(output_text))


class ConsoleBot():
    """console based bot (for testing)"""
    def __init__(self, options):
        self.handler = Handler()
        self.userID = options.userID

    def run(self):
        """main bot loop"""
        while True:
            text = input("Enter a command: ")
            if utils.clean(text, split=False) == "/quit":
                break
            asyncio.run(self.main(text))

    async def main(self, text):
        """sends inpput to handler and prints output"""
        output_text = ""

        # handles messages
        output_text = await self.handler.handle_message(text, console=True, userID=self.userID)

        # sends message to hangouts
        if output_text:
            print(utils.newline(output_text))
