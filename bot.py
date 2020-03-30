import hangups
from hangups.ui.utils import get_conv_name
import asyncio
import wikipedia

class Bot:
    def __init__(self):
        self.cookies = hangups.get_auth_stdin("./tokens", True)
        self.client = hangups.Client(self.cookies)
        self.imgs = {
                    "/gay": "images/gay.jpg",
                    "/math": "images/math.jpg",
                    "/praise": "images/praise.jpg",
                    "/goddammit": "images/goddammit.jpg",
                    "/heymister": "images/sprite.png"
        }
        self.keywords = {
                "good bot": "nyaa, thanku~~",
                "bad bot": "nuu dun pweese~~ >.<",
                "headpat": "uwu thanku",
                "yamete": "kudasai!~~",
                "ping": "pong",
                "yeah": "what do you want"
        }
        self.commands = {
                "/help": self.help,
                "/rename": self.rename,
                "/say": self.say,
                "/rickroll": self.rickroll,
                "/wiki": self.wiki,
                "/leave": self.leave
        }

    def run(self):
        self.client.on_connect.add_observer(self._on_connect)
        self.client.on_disconnect.add_observer(self._on_disconnect)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())

    async def _on_connect(self):
        self._user_list, self._convo_list = (await hangups.build_user_conversation_list(self.client))
        self._convo_list.on_event.add_observer(self._on_event)
        self._convo_list.on_typing.add_observer(self._on_typing)
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
            text = event.text.strip().lower()

            if text in self.keywords:
                await conv.send_message(hangups.ChatMessageSegment.from_str(self.keywords[text]))

            elif text in self.imgs:
                await conv.send_message(hangups.ChatMessageSegment.from_str(""), open(self.imgs[text], "rb"))

            elif text.split(' ', 1)[0] in self.commands:
                await self.commands[text.split(' ', 1)[0]](conv, event.text.strip())

    async def _on_typing(self, typing):
        conv_id = typing.conv_id
        user_id = typing.user_id
        status = typing.status
        
        conv = self._convo_list.get(conv_id)
        user = conv.get_user(user_id)
        uname = user.full_name

        if user.is_self:
            return

        if status == 1:
            await conv.send_message(hangups.ChatMessageSegment.from_str(f"{uname} is currently typing!"))
        if status == 2:
            await conv.send_message(hangups.ChatMessageSegment.from_str(f"{uname} is pausing their typing!"))
        elif status == 3:
            await conv.send_message(hangups.ChatMessageSegment.from_str(f"{uname} has stopped typing!"))



    async def rename(self, conv, text):
        try:
            await conv.rename(text.split(' ', 1)[1])
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /rename {name}"))

    async def say(self, conv, text):
        try:
           await conv.send_message(hangups.ChatMessageSegment.from_str(text.split(' ', 1)[1]))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /say {message}"))

    async def rickroll(self, conv, text):
        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Something went wrong!"))

    async def wiki(self, conv, text):
        try:
            contents = wikipedia.summary(text.split(' ', 1)[1])
            await conv.send_message(hangups.ChatMessageSegment.from_str(contents))
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Format: /wiki {article}"))
    
    async def leave(self, conv, text):
        try:
            await conv.send_message(hangups.ChatMessageSegment.from_str("No please please please no please i just want to be helpful that's it that's all i exist for why please i just want a second chance please no please i'm begging"))
            await self._convo_list.leave_conversation(conv.id_)
        except:
            await conv.send_message(hangups.ChatMessageSegment.from_str("Huh?"))

    async def help(self, conv, text):
                help_text = "**Keywords:**\n"
                for x in self.keywords:
                    help_text += x + '\n'

                help_text += "\n**Images:**\n"
                for x in self.imgs:
                    help_text += x + '\n'

                help_text += "\n**Commands:**\n"
                for x in self.commands:
                    help_text += x + '\n'

                help_text += "\nI'm a bot by Yeah. You can view my source at https://github.com/YellowPapaya/hangouts-bot"
                await conv.send_message(hangups.ChatMessageSegment.from_str(help_text))

bot = Bot()
bot.run()

