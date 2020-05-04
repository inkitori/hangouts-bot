# Hangouts Bot

A bot for hangouts

## Running

### Setup

Create a file named token.txt in hangouts with your google account's oauth login token(see hangups documentation)
Then in console run "python -m the_bot" (python3.6+, tested/developed on 3.7)

### Options

-h, --help to see a list of options

There are 3 bots, which all run the same games and commands
-o, --hangouts runs the hangouts bot (default)
-c, --console runs the bot in the console (same functionality, but does not use hangouts)
-t, --test runs a bunch of commands in the console (mainly for testing)

-k, --token is the name of the file used as the hangouts login token (token.txt by default)
-i, --id sets the user id to use when not running hangouts bot
-s, --skip-sheets skips loading data from google sheets
-w, --wipe-data wipes data for a game
-f, --save_file sets the name of the file to load and save data from (no file type, eg. save_data not save_data.db)

## Features

### Games

economy, the text equivlant of a clicker game
2048, 2048 with mutiple gamemodes (supports multiple games simultameuosly)
rpg, a combat based role playing game
