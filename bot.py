import hangups
from hangups.ui.utils import get_conv_name
import asyncio
from handler import Handler


class Bot:
    def __init__(self):
        self.cookies = hangups.get_auth_stdin("/home/chendi/.cache/hangups/refresh_token.txt", True)
        self.client = hangups.Client(self.cookies)
        self.handler = Handler()

    def run(self):
        self.client.on_connect.add_observer(self._on_connect)
        self.client.on_disconnect.add_observer(self._on_disconnect)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())

    async def _on_connect(self):
        self._user_list, self._convo_list = (await hangups.build_user_conversation_list(self.client))
        self._convo_list.on_event.add_observer(self._on_event)
        convs = self._convo_list.get_all()

        for c in convs:
            print(get_conv_name(c))

    async def _on_disconnect(self):
        print("ded")

    async def _on_event(self, event):
        conv_id = event.conversation_id
        conv = self._convo_list.get(conv_id)
        user_id = event.user_id
        user = conv.get_user(user_id)

        if isinstance(event, hangups.ChatMessageEvent) and (not user.is_self):
            strippedText = event.text.strip().lower()

            if strippedText in self.handler.keywords:
                await conv.send_message(toSeg(self.handler.keywords[strippedText]))

            elif strippedText.split()[0] in self.handler.images:
                f = open(self.handler.images[strippedText.split()[0]], "rb")
                await conv.send_message(toSeg(""), f)
                f.close()

            elif strippedText.split()[0] in self.handler.commands:
                await self.handler.commands[strippedText.split()[0]](self, event)

        elif isinstance(event, hangups.MembershipChangeEvent):
            if conv.get_user(event.participant_ids[0]).is_self and event.type_ == 1:
                await conv.send_message(toSeg("Saber in!"))


def toSeg(text):
    return hangups.ChatMessageSegment.from_str(text)


bot = Bot()
bot.run()
