import hangups
import asyncio
import random


chendi_responses = (
    "...", "meep", "wat", "much confuzlment", "im bored", "hrm", "hm",
    "mhm", "maybe", "doi", "aww", "HAH", "one min", "ur crazy", "Joseph,\nno",
    "how's life?", "the heck", "AHHH", "MEEP", "mep", "sleep", "snip", "SNIP",
    "Sarah,\nno", "wdym"
)


class Bot:

    properties = {
        "annoying": False, "quiet": False
    }

    def chendi(self):
        return random.choice(chendi_responses)

    def set_property(self, bot_property):
        property = bot_property[1]
        self.properties[property] = bot_property[2][0].lower() == "t"
        return self.properties[property]
    set_property.need_to_await = False

    async def leave(self, text):
        await self.client.disconnect()
    leave.need_to_await = True

    text_responses = {
        "good_bot": "meep",
        "bad_bot": "MEEP",
        "meep": "meep",
    }

    responses = {
        "say_something": chendi,
    }

    commands = {
        "leave": leave,
        "set": set_property,
    }

    def __init__(self):
        self.cookies = hangups.get_auth_stdin("/home/chendi/.cache/hangups/refresh_token.txt", True)
        self.client = hangups.Client(self.cookies)

    def run(self):
        self.client.on_connect.add_observer(self._on_connect)
        self.client.on_disconnect.add_observer(self._on_disconnect)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())

    async def _on_typing(self, typing):
        if not self.properties["annoying"]:
            return
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

    async def _on_connect(self):
        self._user_list, self._convo_list = (await hangups.build_user_conversation_list(self.client))
        self._convo_list.on_event.add_observer(self._on_event)
        self._convo_list.on_typing.add_observer(self._on_typing)
        # convs = self._convo_list.get_all()

    async def _on_disconnect(self):
        pass

    async def _on_event(self, event):
        conv_id = event.conversation_id
        conv = self._convo_list.get(conv_id)
        user_id = event.user_id
        user = conv.get_user(user_id)

        if isinstance(event, hangups.ChatMessageEvent) and (not user.is_self):
            text = event.text.strip().lower().split()
            text_1 = text[0]

            if text_1 in self.text_responses and not self.properties["quiet"]:
                await conv.send_message(hangups.ChatMessageSegment.from_str(self.text_responses[text_1]))
            elif text_1 in self.responses and not self.properties["quiet"]:
                message = self.responses[text_1](self)
                await conv.send_message(hangups.ChatMessageSegment.from_str(message))
            elif text_1 in self.commands:
                command = self.commands[text_1]
                if command.need_to_await:
                    await command(self, text)
                else:
                    command(self, text)


bot = Bot()
bot.run()
