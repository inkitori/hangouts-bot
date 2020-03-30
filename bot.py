import hangups
from hangups.ui.utils import get_conv_name
import asyncio

class Bot:
    def __init__(self):
        self.cookies = hangups.get_auth_stdin("./tokens", True)
        self.client = hangups.Client(self.cookies)
        self.imgs = {
                    "/gay": open("images/math.jpg", "rb"),
                    "/math": open("images/math.jpg", "rb"),
                    "/praise": open("images/praise.jpg", "rb"),
                    "/goddammit": open("images/goddammit.jpg", "rb")
        }
        self.keywords = {
                "good bot": "nyaa, thanku~~",
                "bad bot": "nuu dun pweese~~ >.<",
                "bot": "ok"
        }

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
        print("bye")

    async def _on_event(self, event):
        conv_id = event.conversation_id
        conv = self._convo_list.get(conv_id)
        
        if isinstance(event, hangups.ChatMessageEvent):
            text = event.text.strip().lower()
            print(text + " " + conv.get_user(event.user_id).full_name)

            if text in self.keywords:
                await conv.send_message(hangups.ChatMessageSegment.from_str(self.keywords[text]))
            elif text in self.imgs:
                await conv.send_message(hangups.ChatMessageSegment.from_str(""), self.imgs[text])
            elif text == "/help":
                help_text = "**Keywords:**\n"
                for x in self.keywords:
                    help_text += x + '\n'
                help_text += "\n**Images:**\n"
                for x in self.imgs:
                    help_text += x + '\n'
                await conv.send_message(hangups.ChatMessageSegment.from_str(help_text))

bot = Bot()
bot.run()

