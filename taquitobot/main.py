"""
main.py

Entry point for discord bot features.


"""
import argparse
import discord
from discord.ext import commands
import logging
from custom_secrets import (
    TEST_BOT_TOKEN, random_response
)
from music_commands.music import MusicCommands

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()

file_handler = logging.FileHandler(filename="discord.log", mode="w")
file_handler.setLevel(logging.WARNING)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.load_extension("music_commands.music")

@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        return None
    
    if message.author.bot:
        return None
    
    await bot.process_commands(message)

    message_content = message.content.lower()
    response = random_response(message=message_content)
    
    if response:
        await message.channel.send(response)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        print("Debug mode enabled")
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    bot.run(token=TEST_BOT_TOKEN, log_handler=file_handler)
