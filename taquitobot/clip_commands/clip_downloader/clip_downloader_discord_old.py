"""
clip_downloader_discord.py

Class implementation for a ClipDownloaderDiscord to take text from discord
and download the video.

Attributes:
    OUTPLAYED_PATTERN (str): Regex to represent an outplayed.tv link to easily
        find and parse a discord message for the link.

TODO:

Versioning:
    Author: Aidan (ChimichangaKid)
    Date: 2024-07-25
    Version: 1.0.0

Notes:
    Private attributes are documented to assist in understanding the importance
    of variables in the design process as well as to assist with remembering
    for future updates.
"""

import re
import requests
from bs4 import BeautifulSoup
from .clip_downloader_abstract import ClipDownloaderWebLinkAbstract

OUTPLAYED_PATTERN = r"https://outplayed\.tv/.*"


class ClipDownloaderDiscord(ClipDownloaderWebLinkAbstract):
    """
    Class to handle parsing of the discord message, finding the clip url and
    then storing the information related to the name of the game as well as the
    future title of the video.

    Args:
        discord_message (str): The discord message that was sent to trigger
            this code as a string.
    """

    """
    Private Attributes:
        _video_title (str): The title of the video that was set by the user in
            the discord message.
        _game_title (str): The title of the game that is associated with the
            posted url as a string.
        _web_link (str): The link to the video on the web.
    """

    def __init__(self, discord_message: str) -> None:
        self._video_title = re.sub(
            OUTPLAYED_PATTERN, "", discord_message, re.IGNORECASE
        ).replace("\n", "")
        self._game_title = ""
        self._web_link = ""
        self._modify_web_link(discord_message)

    def get_game_title(self) -> str:
        """
        Method to get the title of the game that is being clipped.

        Returns:
            (str): The title of the video as a string.
        """
        return self._game_title

    def get_video_title(self) -> str:
        """
        Method to download the video from a file.

        Returns
            (str): The title of the game as a string.
        """
        return self._video_title

    def _modify_web_link(self, discord_message: str) -> None:
        """
        Helper function to modify the web link based on the given discord
        message as well as to find information about the video.

        Args:
            discord_message (str): The discord message that was sent to
            provoke this process.
        """
        video_url = re.search(OUTPLAYED_PATTERN, discord_message).group()
        url_string = requests.get(video_url)
        html = url_string.text
        soup = BeautifulSoup(html, "html.parser")

        video_tag = soup.find("video")
        self._web_link = video_tag["src"]
        title_tag = soup.find("title")
        outplayed_tag = title_tag.get_text().split("|")
        try:
            self._game_title = outplayed_tag[0].split("#")[1].replace(" ", "")
        except:
            self._game_title = "Valorant"
        return

    def _get_mp4_link(self, soup: BeautifulSoup):
        """
        Helper function to get the mp4 link from the BeautifulSoup parsed
        html.

        Args:
            soup (BeautifulSoup): BeautifulSoup parsed html to find the video
                link from.
        """
        video_tag = soup.find("video")
        self._web_link = video_tag["src"]

    def _get_game_title(self, soup: BeautifulSoup):
        """
        Helper function to get the game title from the BeautifulSoup parsed
        html.

        Args:
            soup (BeautifulSoup): BeautifulSoup parsed html to find the game
                title from.
        """
        title_tag = soup.find("title")
        outplayed_tag = title_tag.get_text().split("|")
        try:
            self._game_title = outplayed_tag[0].split("#")[1].replace(" ", "")
        except:
            self._game_title = "Valorant"
