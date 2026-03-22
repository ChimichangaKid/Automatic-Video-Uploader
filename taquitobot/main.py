"""
main.py

Entry point for discord bot features.


"""
import argparse
import discord
from discord.ext import commands
import logging
from custom_secrets import (
    TEST_BOT_TOKEN, random_response, BOT_TOKEN
)
from re import search, IGNORECASE

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

OUTPLAYED_PATTERN = r"https://outplayed\.tv/.*"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if "music_commands.music" not in bot.extensions:
        await bot.load_extension("music_commands.music")

@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        return None
    
    if message.author.bot:
        return None
    
    await bot.process_commands(message)

    message_content = message.content
    
    
    if search(pattern=OUTPLAYED_PATTERN, string=message_content, flags=IGNORECASE):
        clip_downloader = ClipDownloaderDiscord(discord_message=message_content)
        file_name = clip_downloader.download_video()
        game_title = clip_downloader.get_game_title()
        video_title = clip_downloader.get_video_title()
        print("Made it to ")
        match game_title:
            case "Valorant":
                clip_prep = ClipPrepValorant(video_file=file_name)
            case "LeagueofLegends":
                clip_prep = ClipPrepLeagueOfLegends(video_file=file_name)
            case _:
                clip_prep = ClipPrepValorant(video_file=file_name)
        clip_editor = ClipEditor(clip_prep=clip_prep)
        print("made it to clip editor")
        edited_clip = clip_editor.edit_and_save_video(clip_file=file_name,
                                                      game_title=game_title,
                                                      video_title=video_title)
        
        print("made it to clip_uploader")
        clip_uploader = YouTubeUploader(video_title=video_title,
                                        game_title=game_title)
        
        try:
            video_link = clip_uploader.upload_to_youtube(file_name=edited_clip)
            await message.channel.send(video_link)
        except Exception as e:
            print(f"Error uploading video {e}")
        finally:
            clip_editor.remove_footage(clip=edited_clip)
            clip_editor.remove_footage(clip=file_name)
    
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

    bot.run(token=BOT_TOKEN, log_handler=stream_handler)
