# Hangouts Bot

A bot for hangouts (but also the console). Has a few games, and a chatbot. Currently getting wrapped up, soon to be abandoned

## Running

### Setup

Create a file named token.txt in hangouts with your google account's oauth login token(see hangups documentation)
RPG relies on loading data from [this google sheet](https://docs.google.com/spreadsheets/d/1H9m57A7vcSvGnEIrAKAHjg-GmvKw1GqQqQdAMeuN5do/).
To load it, you will need access to the google sheets api. TO setup, create a google cloud project with the google sheets api (see sheets api quickstart).
Download configuration.json into the root directory. If you do not want to load the data, use the -s flag.
If you want to use custom data, replace the sheet ID and name in RPG manager and add named ranges(see the sheet for layout)
Then in console run "python -m the_bot" (python3.6+, tested/developed on 3.7)
use the id command from the account you want to bot on and add to bot.Bot.ignore to avoid the bot triggering itself or other copies of the bot

### Usage

Then in console run "python -m the_bot" (python3.6+, tested/developed on 3.7)
For the hangouts bot, wait until "Connected!" is printed in console before sending messages to hangouts

### Dependencies

For using hangouts: hangups  
For loading items/rooms in RPG from google sheets: googleapiclient, google_auth_oauthlib, google (check google sheets api for installation details)
For GTP2 bot: torch, pytorch-ignite, transformers

### Options

-h, --help to see a list of options

There are 3 bots, which all run the same games and commands  
-o, --hangouts runs the hangouts bot (default)  
-c, --console runs the bot in the console (same functionality, but does not use hangouts)  
-t, --test runs a bunch of commands in the console (mainly for testing)  

-k, --token is the name of the file used as the hangouts login token (token.txt by default)  
-i, --id sets the user id to use when running console bot
-s, --skip-sheets skips loading data from google sheets  
-w, --wipe-data wipes data for a game (eco, rpg, 2048)
-f, --save_file sets the name of the file to load and save data from (no file type, eg. save_data not save_data.db)  

## Features

### Games

economy, the text equivlant of a clicker game  
2048, 2048 with mutiple gamemodes adapted from Creonalia's pygame GUI version (supports multiple games simultameuosly)  
rpg, a combat based role playing game  

### GPT2 Chatbot

Note that due to issues with python version compatibility, the chatbot is not currently connected to the main bot and can be run by running gpt2_chatbot/chatbot.py. Works on 3.6 but not 3.7.

We changed a bit of the [OpenAI GPT2 bot](https://github.com/huggingface/pytorch-openai-transformer-lm) which was derived from the [OpenAI GPT2 model](https://openai.com/blog/better-language-models/) to plug into our chatbot. It's located in `./the-bot/gpt2-chatbot`.

If you run the bot as in the repo, it will generate a file called `dataset_cache_OpenAIGPTTokenizer` to cache the pretrained model. If you want to skip this step, you can download [this file](https://drive.google.com/file/d/1665mjdwVi2vn8lpLET4M_fnh-cyAftHw/view?usp=sharing.). Copy the file into `./the-bot/gpt2-chatbot`.

## Extending

This bot is complete, but unfinished. Plenty of features were never added due to time constraints, and there's plenty of room for add-ons.

### Code Structure

Getting text input is entirely handled by the bots. The input is handled internally by Handler, and is passed as a generator, utils.command_parser(), which yields one word at a time.

Games are made up of a manager and one or more classes. Managers call methods on other objects and save/load data. Games store players by their hangouts use. Groups of objects are generally global dictionaries at the bottom of the file the class is defined in. Players are stored by hangouts userid, while other objects are stored by name.

### Code Flow

main.py gets the command line arguments from config.py, and runs the bot(hangouts, console, or test). The bot gets the text and sends it to handler.Handler. Handler splits the code and runs the appropriate command. Commands for hangouts are handled in the Handler, or passed into the appropriate game manager.

### File Organization

Any files that are not code go in the root directory. Images go in the images folder. Code is in the_bot. Bot code and shared code is in the_bot, while each game has a folder in the_bot, and the chatbot has its own folder.


### Adding Commands

Commands are either coded directly in an if elif chain, or in a dict with their corrosponding function. All the functions in a dict take the same arguments, so when adding copy in the arguments from another function in that dict.

### Adding Games

Games all have a gamemanager stored in Handler. Gamemanagers must have a run_game and a save_game function which is called in Handler.play_game(). Run game takes the user_id and commands generator as arguments.

### Possible Features

these are features which were considered and/or partially implemented, but never added. an easy jumping off point for extending

#### RPG

party commands - impllemented, but commented out because of bugs we did not have the time or commitment to fix
atuofight- fights for a player automatically (already in Player.options)
rpg.classes.Room.generate_encounter() - intended to be an extension of generate_enemy() to account for large party sizes, but never finished
the method is defined, but has no body and is never called. should be called in place of generate_enemy()  
rpg.player_class.inventory.add() - this works fine, but was never supposed to be a command.currently, any item can be added if the player knows the name. this should be changed to only allow players to pick up items in the room_data  
rpg.classes.Room.drops - stored, but never used. should let player pick up the items after defeating the boss  
a commmand to view item details - add a command to inventory to view item details (probably by using item.stats.print_stats() and utils.join_items)  
rpg.classes.ItemModifiers - fully implemented, but there is no way to change it. add a reforge command to upgrade the modifier, probably costing some money  
rpg.classes.Room.boss - stored, but never used. should drop Room.drops upon defeat and allow progression to the next level  
a status command - print out current room, currently fighting, current party, etc.  
fix group warping - only th party leader can warp. when they warp, all other party members should warp as well  

#### Economy

More item types - there is code in place to deal with extra item types in the shop and inventory, but there is only 1 type  
balance - the game was never proparly balanced since we didn't know how to balance it  
