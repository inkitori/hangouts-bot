"""
for testing random stuff
"""
import utils
import asyncio


def test(bot):
    test_commands = {
        "/rpg": "profile"
    }
    for prefix, command in test_commands.items():
        asyncio.run(bot.main(f"{prefix} {command}"))
