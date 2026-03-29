""" """

import logging
import random
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
from moviepy import VideoFileClip

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] in %(name)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

MUSIC_FOLDER_PATH: Path = Path(__file__).parent.resolve() / "music"
OVERLAY_FOLDER_PATH: Path = Path(__file__).parent.resolve() / "overlays"


class AbstractClipPrep(ABC):
    def __init__(self, video_file: Path):
        self._song_path: Path | None = None
        self._first_highlight_time: float = 0
        self._song_drop_time: float = 0
        self._overlay_path: Path | None = None
        self._last_highlight_time: float = 0
        self._overlay_drop_time: float = 0

        self._video_file: Path = video_file

    def randomize_song(self) -> None:
        songs: list[Path] = [
            song for song in MUSIC_FOLDER_PATH.iterdir() if song.is_file()
        ]

        self._song_path = random.choice(songs)
        logger.info(f"The randomly chosen song was {self._song_path}")
        self._song_drop_time = float(
            self._song_path.name.split(sep="_")[0].replace("$", ".")
        )
        logger.info(f"The overlay drop time is {self._song_drop_time}")

    def randomize_overlay(self) -> None:
        if random.randint(a=0, b=7) != 5:
            logger.info("No overlay chosen for this video")
            self._overlay_path = None
            return

        overlays: list[Path] = [
            overlay for overlay in OVERLAY_FOLDER_PATH.iterdir() if overlay.is_file()
        ]

        self._overlay_path = random.choice(overlays)
        logger.info(f"The randomly chosen overlay was {self._overlay_path}")
        self._overlay_drop_time = float(
            self._overlay_path.name.split(sep="_")[0].replace(old="$", new=".")
        )
        logger.info(f"The overlay drop time is {self._overlay_drop_time}")

    @abstractmethod
    def find_highlight_times(self) -> None: ...

    @property
    def song_path(self) -> Path | None:
        return self._song_path

    @property
    def first_highlight_time(self) -> float:
        return self._first_highlight_time

    @property
    def song_drop_time(self) -> float:
        return self._song_drop_time

    @property
    def overlay_path(self) -> Path | None:
        return self._overlay_path

    @property
    def last_highlight_time(self) -> float:
        return self._last_highlight_time

    @property
    def overlay_drop_time(self) -> float:
        return self._overlay_drop_time


class ValorantClipPrep(AbstractClipPrep):
    __CROP_MAP: dict[str, int] = {"top": 805, "bottom": 920, "left": 905, "right": 1015}
    __TIME_BETWEEN_FRAME_READS_SEC: float = 0.25
    __TIME_TO_WAIT_AFTER_FINDING: int = 2
    __CLIP_DELAY_OFFSET: float = 0.35
    __DEFAULT_START_TIME: int = 3

    def __init__(self, video_file: Path):
        super().__init__(video_file)

    def find_highlight_times(self) -> None:

        video_capture: VideoFileClip = VideoFileClip(self._video_file)
        video_capture = video_capture.cropped(
            x1=self.__CROP_MAP["left"],
            y1=self.__CROP_MAP["top"],
            x2=self.__CROP_MAP["right"],
            y2=self.__CROP_MAP["bottom"],
        )
        logger.info(f"Analyzing video file {self._video_file}")
        time_interval: float = 0
        highlights: list[float] = []
        while time_interval < video_capture.duration:
            colour = cv2.cvtColor(
                video_capture.get_frame(time_interval), cv2.COLOR_RGB2BGR
            )
            grayscale = cv2.cvtColor(colour, cv2.COLOR_BGR2GRAY)

            circles = cv2.HoughCircles(
                image=grayscale,
                method=cv2.HOUGH_GRADIENT,
                dp=1.5,
                minDist=100,
                minRadius=40,
                maxRadius=60,
            )

            if circles is not None:
                logger.info(f"Found highlight at time {time_interval}")
                highlights.append(time_interval - self.__CLIP_DELAY_OFFSET)
                time_interval += self.__TIME_TO_WAIT_AFTER_FINDING
            else:
                time_interval += self.__TIME_BETWEEN_FRAME_READS_SEC

        logger.info(f"Found highlights at times: {highlights}")
        try:
            self._first_highlight_time = highlights[0]
            self._last_highlight_time = highlights[-1]
        except IndexError:
            logger.info("Found no highlights")
            self._first_highlight_time = self.__DEFAULT_START_TIME
            self._last_highlight_time = self.__DEFAULT_START_TIME


class LeagueClipPrep(AbstractClipPrep): ...
