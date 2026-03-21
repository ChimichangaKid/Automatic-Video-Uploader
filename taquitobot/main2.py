"""
main.py

Control script for interfacing with bot commands using discord.py package. 

Attributes:
    intents (discord.Intents): Discord intents object that sets permissions for 
        the bot.
    bot (discord.ext.commands.Bot): Discord bot object to attach commands.
    outplayed_pattern (str): Regex string containing the outplayed.tv link for 
        automatic video uploading.

TODO:
    - Write tests
    - Modularize code

Versioning
    Author: Aidan (Chimichanga Kid)
    Date: 2024-07-21
    Version 1.2.2

Notes:
    Documentation reference can be found at 
    https://discordpy.readthedocs.io/en/stable/.
    Code documentation follows Google Python Style Guide when possible. See 
    https://google.github.io/styleguide/pyguide.html for details.
"""
import os
import asyncio
import re
import nest_asyncio
import discord
from discord.ext import commands
from clip_commands.clip_downloader.clip_downloader_discord import (
    ClipDownloaderDiscord
)
from clip_commands.clip_editor.clip_prep import (
    ClipPrepValorant,
    ClipPrepLeagueOfLegends
)
from clip_commands.clip_editor.clip_editor import (
    ClipEditor
)
from clip_commands.clip_uploader.clip_uploader import (
    YouTubeUploader
)


nest_asyncio.apply()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)
outplayed_pattern = r"https://outplayed\.tv/media/.*"


@bot.event
async def on_ready():
    """
    Event to inform the user when the bot has logged in and is ready to receive
    commands.
    """
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    """
    Behavior for when a message is received in a discord server. 
    
    Args:
        message (discord.Message): The message that was sent in the discord 
            channel as a discord.Message object.
    """
    await bot.process_commands(message)
    if message.author == bot.user:
        return None

    content = message.content.lower()

    if re.search(outplayed_pattern, content, re.IGNORECASE):
        clip_downloader = ClipDownloaderDiscord(discord_message=content)
        file_name = clip_downloader.download_video()
        game_title = clip_downloader.get_game_title()
        video_title = clip_downloader.get_video_title()
        match game_title:
            case "valorant":
                clip_prep = ClipPrepValorant(video_file=file_name)
            case "leagueoflegends":
                clip_prep = ClipPrepLeagueOfLegends(video_file=file_name)
            case _:
                clip_prep = ClipPrepValorant(video_file=file_name)

        clip_editor = ClipEditor(clip_prep=clip_prep)  
        edited_clip = clip_editor.edit_and_save_video(clip_file=file_name, 
                                                      game_title=game_title,
                                                      video_title=video_title)
        
        clip_uploader = YouTubeUploader(video_title=video_title,
                                        game_title=game_title)
        try:
            clip_uploader.upload_to_youtube(file_name=edited_clip)
        except:
            print("error uploading video")
        finally:
            clip_editor.remove_footage(edited_clip)


async def load():
    """
    Functions to load the cogs that are used for commands.
    """
    await bot.load_extension("music_commands.music_commands")
    await bot.load_extension("riot.riot_requests")


async def main():
    """
    Main function to start the bot and initialize the control loop.
    """
    async with bot:
        await load()
        try:
            await bot.run(os.environ['Discord_test_token'])
        except:
            os.system("kill 1")


if __name__ == '__main__':
    asyncio.run(main())
