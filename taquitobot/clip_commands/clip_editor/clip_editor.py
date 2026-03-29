""" """

import logging
from pathlib import Path

from moviepy import AudioFileClip, VideoFileClip

from taquitobot.clip_commands.clip_downloader.clip_downloader import (
    AbstractClipDownload,
)
from taquitobot.clip_commands.clip_editor.clip_prep import AbstractClipPrep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] in %(name)s - %(message)s"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


class ClipEditor:
    __ASPECT_HEIGHT: int = 960
    __ASPECT_WIDTH: int = 540

    def __init__(
        self, clip_prep: AbstractClipPrep, clip_downloader: AbstractClipDownload
    ) -> None:

        self.__clip_prep: AbstractClipPrep = clip_prep
        self.__clip_downloader: AbstractClipDownload = clip_downloader

        self.__audio = self.__clip_downloader.game_title != "LethalCompany"

        self.__edited_file_name: Path = (
            Path(__file__).parent / f"{self.__clip_downloader.game_title}_"
            f"{self.__clip_downloader.video_title}_"
            "tiktok_reels_shorts.mp4"
        )

    def edit_video(self) -> None:
        logger.info("Configuring clips for editting")
        logger.info(f"Paths are {self.__clip_downloader.clip_file}")
        video_clip = VideoFileClip(str(self.__clip_downloader.clip_file))
        audio_clip = AudioFileClip(self.__clip_prep.song_path)

        clip_duration: float = video_clip.duration

        song_start_time = (
            self.__clip_prep.song_drop_time - self.__clip_prep.first_highlight_time
        )

        audio_clip = audio_clip.subclipped(
            song_start_time, song_start_time + clip_duration
        )

        if self.__audio:
            logger.info("Setting audio to song")
            video_clip = video_clip.with_audio(audio_clip)

        video_clip = video_clip.resized(
            height=self.__ASPECT_HEIGHT, width=self.__ASPECT_WIDTH
        )

        video_clip.write_videofile(
            filename=self.__edited_file_name,
            fps=24,
            codec="libx264",
            preset="ultrafast",
            logger="bar",
        )

    @property
    def edited_file_name(self) -> Path | None:
        return self.__edited_file_name
