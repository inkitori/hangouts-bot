"""
bot for hangouts
"""
from handler import Handler
import hangups
import asyncio
import utils
import sys


class Bot:
    """bot for hangouts (normal use case)"""

    ignore = (
        105849946242372037157,  # odlebot
        11470746254329358783,  # saberbot
        104687919952293193271,  # Ether(chendibot)
    )

    def __init__(self, args):
        self.cookies = hangups.get_auth_stdin(args.token, True)
        self.client = hangups.Client(self.cookies)
        self.handler = Handler(load_sheets=args.load_sheets)

    def run(self):
        """main loop for running bot"""
        self.client.on_connect.add_observer(self._on_connect)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.connect())
        sys.exit(0)

    async def _on_connect(self):
        """called when bot connects to hangouts"""
        self._user_list, self._convo_list = (
            await hangups.build_user_conversation_list(self.client)
        )
        self._convo_list.on_event.add_observer(self._on_event)
        print("Connected!")

    async def _on_event(self, event):
        """called when there is an event in hangouts"""
        user, conv = utils.get_user_and_conv(self._convo_list, event)
        output_text = ""

        if user.is_self or utils.user_in(self.ignore, user):
            return

        # handles messages
        if (isinstance(event, hangups.ChatMessageEvent)):
            output_text = await self.handler.handle_message(event, bot=self)

        # sends message to hangouts
        if output_text:
            await conv.send_message(utils.to_seg(output_text))

    async def send_image(self, image, conv):
        await conv.send_message(utils.to_seg(""), image)

    async def rename_conv(self, new_name, conv):
        await conv.rename(new_name)
        return "Sucessfully renamed"

    async def quit(self):
        await self.client.disconnect()


class ConsoleBot:
    """console based bot (for testing)"""

    def __init__(self, args):
        self.handler = Handler(console=True, load_sheets=args.load_sheets)
        self.user_id = args.user_id

    def run(self):
        """main bot loop"""
        while True:
            text = input("Enter a command: ")
            if utils.clean(text, split=False) == "/quit":
                break
            asyncio.run(self.main(text))

    async def main(self, text):
        """sends input to handler and prints output"""
        output_text = await self.handler.handle_message(text, user_id=self.user_id)

        if output_text:
            print(utils.newline(output_text))


class TestBot:
    """bot for testing commands"""

    def __init__(self, args):
        self.handler = Handler(console=True, load_sheets=args.load_sheets)
        self.user_id = args.user_id
        self.commands = {
            "economy": (
                "register testbot",
                "leaderboard", "shop", "profile",
                "mine", "mine", "mine", "mine",
                "buy tin pick", "prestige", "prestige_upgrade", "give 101 1"
            ),
            "2048": (
                "create testgame", "rename testgame test", "games",
                "create qwed", "delete qwed", "test u", "<", "v", "l",
                "confusion", "eleven", "restart", "sggstaer", "gamemodes",
                "move", "scores", "reserved",
            ),
            "rpg": (
                "register testbot", "profile",
                "add starter armor", "add starter weapon",
                "equip boring starter weapon", "equip boring starter armor",
                "inventory",
                "unequip boring starter armor", "remove boring starter armor",
                "warp village", "rest", "warp potatoland",
                "attack", "attack", "attack", "attack", "attack",
                "heal",
            ),
        }

    def run(self):
        """main bot loop"""
        for prefix, commands in self.commands.items():
            print(f"====={prefix.upper()}=====")
            for command in commands:
                command = f"{prefix} {command}"
                print(f"running command {command}")
                asyncio.run(self.main(command))

    async def main(self, text):
        """sends inpput to handler and prints output"""
        output_text = await self.handler.handle_message(text, user_id=self.user_id)
        print(utils.newline(output_text))


bots = {
    "hangouts": Bot,
    "console": ConsoleBot,
    "test": TestBot
}
