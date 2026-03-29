""" """

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] in %(name)s - %(message)s"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


class AbstractClipDownload(ABC):
    def __init__(self, message: str) -> None:
        self._clip_file: Path | None = None
        self._game_title: str = "Gaming"
        self._video_title: str = ""

        self._message: str = message

    @property
    def clip_file(self) -> Path:
        return self._clip_file

    @property
    def game_title(self) -> str:
        return self._game_title

    @property
    def video_title(self) -> str:
        return self._video_title

    @abstractmethod
    def download_video(self) -> None: ...

    @abstractmethod
    def _find_clip_information(self) -> None: ...

    @abstractmethod
    def _find_video_title(self) -> None: ...


class DiscordClipDownload(AbstractClipDownload):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.__video_source_url: str = ""

        self._find_clip_information()
        self._find_video_title()

    def download_video(self, file_path: Path) -> None:
        logger.info(f"Saving video to {file_path}")

        video = requests.get(self.__video_source_url)

        with file_path.open("wb") as f:
            for chunk in video.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        logger.info(f"Completed writing video to {file_path}")
        self._clip_file = file_path

    def _find_clip_information(self) -> None:
        outplayed_url: str = self._message.split(sep="\n")[1]
        logger.info(f"Outplayed URL is {outplayed_url}")

        web_page: requests.Response = requests.get(url=outplayed_url)
        soup: BeautifulSoup = BeautifulSoup(web_page.content, "html.parser")

        self.__video_source_url = str(soup.find(name="video")["src"])
        logger.info(f"Video Source is {self.__video_source_url}")

        # example title: Highlight #Valorant | Captured by #Outplayed
        # splitting gets the second word, then trims the # from the front
        outplayed_title = str(soup.find(name="title").get_text())
        game_title = outplayed_title.split()[1][1:]
        if game_title:
            self._game_title = game_title
        logger.info(f"Game title is {self._game_title}")

    def _find_video_title(self) -> None:
        self._video_title = self._message.split(sep="\n")[0]
        logger.info(f"Video title was found to be {self._video_title}")
