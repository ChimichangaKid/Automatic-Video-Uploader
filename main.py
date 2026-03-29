"""
main.py

Entry point for discord bot features.


"""

import argparse
import logging
from re import IGNORECASE, search

import discord
from taquitobot.custom_secrets import (
    BOT_TOKEN,
    TEST_BOT_TOKEN,  # noqa: F401
    random_response,
)
from discord.ext import commands

from taquitobot.clip_commands.clip_manager import ClipManager

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] in %(name)s - %(message)s"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

OUTPLAYED_PATTERN = r"https://outplayed\.tv/.*"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if "taquitobot.music_commands.music" not in bot.extensions:
        await bot.load_extension("taquitobot.music_commands.music")


@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        return

    if message.author.bot:
        return

    await bot.process_commands(message)

    message_content = message.content

    if search(pattern=OUTPLAYED_PATTERN, string=message_content, flags=IGNORECASE):
       clip_manager = ClipManager(message_content)
       link = clip_manager.create_video()
       await message.channel.send(link)

    response = random_response(message=message_content.lower())

    if response:
        await message.channel.send(response)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        print("Debug mode enabled")
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    bot.run(token=BOT_TOKEN)
