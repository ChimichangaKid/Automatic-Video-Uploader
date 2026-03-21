"""
"""
import yt_dlp
import discord
import logging
from discord.ext import commands
from collections import deque

logger = logging.getLogger(__name__)

ytdl_opts = {
    'format':
    'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class MusicCommands(commands.Cog):
    """
    Docstring for MusicCommands
    """

    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot
        self._guilds_connected: dict[int, discord.VoiceClient] = {}

        self._song_queue: deque = deque()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logger.info("Music Commands ready")
        print("Music Commands ready")

    @commands.command(name="play", aliases=("p", "P"))
    async def play(self, ctx: commands.Context) -> None:
        """
        Plays the song specified by the message in ctx.message.content.
        
        :param ctx: Discord context for the command that was sent. 
        :type ctx: commands.Context
        """

        if not self._is_connected(guild=ctx.guild):
            connected = await self._connect_to_call(ctx=ctx)

        song_request = ctx.message.content.split(None, 1)[1]

        song_title, song_url = self._get_song_from_yt(song_name=song_request)

        if song_url is None:
            await ctx.channel.send("Error fetching song from YouTube.")
            logger.error("Error fetching song from YouTube.")
            return
        
        self._add_to_queue(song_title=song_title, song_url=song_url)
        
        voice_channel = self._guilds_connected[ctx.guild.id]
        if not voice_channel.is_playing():
            self._play_song(ctx=ctx)

        return
    
    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context) -> None:
        raise NotImplementedError
    
    @commands.command(name="queue", aliases=["q", "Q"])
    async def queue(self, ctx: commands.Context) -> None:
        raise NotImplementedError
    
    @commands.command(name="skip", aliases=["s", "S"]) 
    async def skip(self, ctx: commands.Context) -> None:
        raise NotImplementedError
    
    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context) -> None:
        raise NotImplementedError
    
    @commands.command(name="remove", aliases=["r", "R"])
    async def remove(self, ctx: commands.Context) -> None:
        raise NotImplementedError

    def _is_connected(self, guild: discord.Guild) -> bool:
        """
        Helper method to see if the bot is connected to a channel in the
        guild.
        
        :param guild: The guild to check if connected to.
        :type guild: discord.Guild
        :return: True if the bot is connected, False if the bot is not 
                 connected
        :rtype: bool
        """
        if guild.id not in self._guilds_connected:
            return False
        
        return self._guilds_connected[guild.id].is_connected()
    
    def _add_to_queue(self, song_title: str, song_url: str) -> None:
        """
        Helper method to add the requested song and its url to the queue. 
        
        :param song_title: The title of the song to that is being added. This
                           is for the purpose of providing a readable output
                           of what is in the queue.
        :type song_title: str
        :param song_url: The url of the song, this will be used by the discord
                         library to play the song.
        :type song_url: str
        """
        self._song_queue.append((song_title, song_url))

    
    async def _connect_to_call(self, ctx: commands.context.Context) -> bool:
        """
        Helper method to connect to the voice call of the user that invoked the
        command.
        
        :param ctx: The discord context under which the command was invoked.
        :type ctx: commands.context.Context
        :return: True if the bot is now connected, False otherwise.
        :rtype: bool
        """
        voice_channel = ctx.author.voice

        if not voice_channel:
            await ctx.channel.send("Please join a voice call to play music.")
            logging.debug("Please join a voice call to play music.")
            return
        
        self._guilds_connected[ctx.guild.id] = await voice_channel.channel.connect()

        return self._guilds_connected[ctx.guild.id].is_connected()
    
    def _play_song(self, ctx: commands.Context) -> None:
        """
        Helper method to play the next song in the queue. This method is also
        a callback to recursively play songs using the discord.VoiceClient.play
        callback.
        
        :param ctx: The discord context under which the command was invoked.
        :type ctx: commands.Context
        """
        if len(self._song_queue) <= 0:
            return
        
        song_title, song_stream = self._song_queue.popleft()

        voice_channel = self._guilds_connected[ctx.guild.id] 

        self._bot.loop.create_task(f"Playing song {song_title}.")

        voice_channel.play(discord.FFmpegOpusAudio(song_stream), 
                           after=self._play_song(ctx=ctx),
                           bitrate=64, signal_type="music")

        
        print(f"song_title is {song_title}, song_url is {song_stream}")
  
    @staticmethod
    def _get_song_from_yt(song_name) -> tuple[str, str]:
        """
        Static helper method to get the requested song from YouTube based on 
        the query from the user invoked command.
        
        :param song_name: The name of the search parameters.
        :return: A tuple containing the name of the video that was found and 
                 a url to the video.
        :rtype: tuple[str, str]
        """
        with yt_dlp.YoutubeDL(ytdl_opts) as yt:
            song_info = yt.extract_info(f"ytsearch:{song_name}", 
                                        download=False)
        return song_info["entries"][0]["title"], ["entries"][0]["url"]


async def setup(bot):
    await bot.add_cog(MusicCommands(bot))