""" """

import logging
from pathlib import Path

from taquitobot.clip_commands.clip_downloader.clip_downloader import DiscordClipDownload
from taquitobot.clip_commands.clip_editor.clip_editor import ClipEditor
from taquitobot.clip_commands.clip_editor.clip_prep import (
    AbstractClipPrep,
    LeagueClipPrep,
    ValorantClipPrep,
)
from taquitobot.clip_commands.clip_uploader.clip_uploader import YouTubeUploader

logger = logging.getLogger(__name__)


class ClipManager:
    def __init__(self, message: str):
        self.__message = message

        self.__clip_downloader: DiscordClipDownload = DiscordClipDownload(
            message=self.__message
        )
        self.__clip_prep: AbstractClipPrep | None = None
        self.__clip_editor: ClipEditor | None = None
        self.__clip_uploader: YouTubeUploader | None = None

    def create_video(self) -> None:

        logger.info("Starting ClipDownloader methods")
        self.__clip_downloader = DiscordClipDownload(self.__message)
        downloaded_clip_path = (
            Path(__file__).parent / f"{self.__clip_downloader.video_title}.mp4"
        )
        self.__clip_downloader.download_video(file_path=downloaded_clip_path)

        logger.info("Starting ClipPrep methods")
        match self.__clip_downloader.game_title:
            case "Valorant":
                self.__clip_editor = ValorantClipPrep(
                    video_file=self.__clip_downloader.clip_file
                )
            case "_":
                # default will be valorant, plans to add more and default in future
                self.__clip_editor = ValorantClipPrep(
                    video_file=self.__clip_downloader.clip_file
                )
        self.__clip_prep.randomize_song()
        self.__clip_prep.randomize_overlay()
        self.__clip_prep.find_highlight_times()

        logger.info("Starting ClipEditor methods")

        self.__clip_editor = ClipEditor(
            clip_prep=self.__clip_prep, clip_downloader=self.__clip_downloader
        )

        self.__clip_editor.edit_video()

        self.__clip_uploader = YouTubeUploader(
            video_title=self.__clip_downloader.video_title,
            game_title=self.__clip_downloader.game_title,
        )
