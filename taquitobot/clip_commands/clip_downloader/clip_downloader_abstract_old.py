"""
clip_downloader_abstract.py

Interface for clip downloader methods to be overriden by subclass. Contains
implementation to download videos from different mediums.

Attributes:

TODO:

Versioning
    Author: Aidan (Chimichanga Kid)
    Date: 2024-07-25
    Version: 1.0.0

Notes:
    Private attributes are documented to assist in understanding the importance
    of variables in the design process as well as to assist with remembering
    for future updates.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

import requests


class VideoDownloader(Protocol):
    """
    Interface for parent class of downloading videos, allows many mediums
    of download if download_video method is implemented.
    """

    def get_video_title(self):
        """
        Method to get the title of the video to be published.
        """
        ...

    def get_game_title(self):
        """
        Method to get the title of the game that is being clipped.
        """
        ...

    def download_video(self):
        """
        Method to download the video from a file.
        """
        ...


class ClipDownloaderWebLinkAbstract(ABC, VideoDownloader):
    """
    Abstract class to implement a video downloader given a web link to the
    file on the internet.

    Args:
        link (str): The link to the file on the internet as a string. Defaults
            to an empty string.

    Attributes:

    """

    """
    Private Attributes:
        _web_link (str): The link to the web page
    """

    def __init__(self, link="") -> None:
        self._file_name = ""
        self._web_link = link
        super.__init__()

    def download_video(self) -> str:
        """
        Overrides the method from parent class to download the video,
        downloads video from the given link from abstract method or link
        given in the constructor.

        Args:

        Returns:
            file_name (str): The name of the file as a string where the video
                was downloaded to.
        """
        self._file_name = Path(self._web_link).name

        r = requests.get(self._web_link)

        with Path(self._file_name).open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return self._file_name

    def get_file_name(self) -> str:
        """
        Method to access the file name attribute.

        Args:

        Returns:
            (str): The path to the file of the clip that is being edited.
        """
        return self._file_name

    @abstractmethod
    def _modify_web_link(self) -> None:
        """
        Abstract method that should allow the user to modify the link from
        any medium.
        """
        ...

    @abstractmethod
    def get_video_title(self) -> str:
        """
        Method to get the title of the game that is being clipped.

        Returns:
            (str): The title of the video as a string.
        """
        ...

    @abstractmethod
    def get_game_title(self) -> str:
        """
        Method to download the video from a file.

        Returns
            (str): The title of the game as a string.
        """
        ...
