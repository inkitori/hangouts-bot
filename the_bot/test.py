"""
for testing random stuff
"""
import bot
import config
import asyncio


def test(bot):
    test_commands = {
        "/rpg": "profile"
    }
    for prefix, command in test_commands.items():
        asyncio.run(bot.main(f"{prefix} {command}"))

if __name__ == "__main__":
    test_options = config.parse_arguments("alt")
    test(bot.bots["console"](test_options))
