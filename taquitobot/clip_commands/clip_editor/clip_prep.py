"""
clip_prep.py

Class implementation to parse the video footage and find the information about
timings as well as audio selection to separate the process from the editor.
This class will contain all the information required for editing the video.

Attributes:
    MUSIC_FOLDER (str): The path to the folder containing the songs as a 
        string.

TODO:

Versioning:
    Author: Aidan (ChimichangaKid)
    Date: 2024-07-25
    Version: 1.0.0

Notes:
    
"""
import moviepy.editor
import cv2
import os
import random
import re
import numpy as np

MUSIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "music/")
FACECAM_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "overlays/")

class ClipPrepAbstract:
    """
    A ClipPrepAbstract is an abstract class to have base methods for preparing
    the video clip to be uploaded to YouTube. This involves choosing the song
    and finding the time of the highlight. The songs that are in the folder 
    should have the format with the timestamp of the beat drop in the title, 
    with the decimal replaced with a dollar sign ($).
    """

    def __init__(self, video_file: str) -> None:
        self._face_cam_start_time = 0
        self._song_start_time = 0
        self._song_name = self._choose_random_song(music_folder=MUSIC_FOLDER)
        self._facecam_clip = self._choose_random_facecam_clip(
            facecam_folder=FACECAM_FOLDER)
        self._highlight_time = self._find_highlight_time(file=video_file)
        if len(self._highlight_time) == 0:
            self._highlight_time.append(3)
    
    def _choose_random_song(self, music_folder: str) -> str:
        """
        Helper function to get a random song form the specified folder.

        Args:
            music_folder (str): Path to the folder containing music to randomly
                select from.
        Returns:
            (str): The title of the song
        """
        song_name = os.path.join(music_folder,
                                 random.choice(os.listdir(music_folder)))
        self._song_start_time = float(
            re.search(r'(\d+\$\d+)', song_name).group(1).replace('$', '.'))
        return os.path.join(MUSIC_FOLDER, song_name)

    def _choose_random_facecam_clip(self, facecam_folder: str) -> str:
        """
        Helper function to get a random facecam clip from the specified folder.
        Only selects 20% of the time.

        Args:
            facecam_folder (str): Path to the folder containing the facecam
                footage to randomly select from.
        Returns:
            (str): The link to the facecam clip if selected, otherwise empty
                string.
        """
        if random.randint(1, 6) == 7:
            face_cam_name = random.choice(os.listdir(facecam_folder))
            self._face_cam_start_time = float(
                        re.search(r'(\d+\$\d+)', 
                        face_cam_name).group(1).replace('$', '.'))
            return os.path.join(FACECAM_FOLDER, face_cam_name)
        else:
            return ""

    def _find_highlight_time(self, file: str) -> list[float]:
        """
        Helper method to find the time of the highlight in the clip. This will
        report the time(s) of the highlights as a list float in seconds. The
        list is in chronological order.

        Args:
            file (str): The clip that is being edited. 

        Returns:
            (list[float]): The times of the highlights in seconds, they will 
                be in ascending order from lowest to highest and at least
                2 seconds apart.
        """
        ...


class ClipPrepValorant(ClipPrepAbstract):
    """
    Specific clip prep for Valorant videos to find the time of the highlight. 
    Has the same features as the Abstract parent class.
    """

    def __init__(self, video_file: str) -> None:
        # Crop to make it easier to find the desired shape, crop is given in
        # pixel coordinates.
        self._left_crop = 905
        self._right_crop = 1015
        self._top_crop = 805
        self._bottom_crop = 920
    
        super().__init__(video_file=video_file)

    def _find_highlight_time(self, file: str) -> list[float]:
        """
        Overrides parent class method, uses the circle from the frame of the
        kill to find the highlight time. The elements are separated by at least
        a difference of two (2) seconds.
        """
        video_clip = moviepy.editor.VideoFileClip(file).crop(self._left_crop,
                                                             self._top_crop,
                                                             self._right_crop,
                                                             self._bottom_crop)
        highlights = []
        time_interval = 0
        while time_interval < video_clip.duration:
            colour = cv2.cvtColor(video_clip.get_frame(time_interval),
                                  cv2.COLOR_RGB2BGR)
            grayscale = cv2.cvtColor(colour, cv2.COLOR_BGR2GRAY)
            circles = cv2.HoughCircles(grayscale, cv2.HOUGH_GRADIENT, 1.5, 100,
                                       minRadius=40, maxRadius=60)
            
            if circles is not None:
                highlights.append(time_interval - 0.35)
                time_interval += 2
                
                # If there is no facecam clip we dont need the last highlight.
                if self._facecam_clip == "":
                    return highlights
            else:
                time_interval += 0.25
            
            if len(highlights) >= 5:
                break

        return highlights

class ClipPrepLeagueOfLegends(ClipPrepAbstract):
    """
    Specific clip prep for LoL videos to find the time of the highlight. 
    Has the same features as the Abstract parent class.
    """

    def __init__(self, video_file: str) -> None:
        self._left_crop = 1785
        self._top_crop = 243
        self._right_crop = 1840
        self._bottom_crop = 450
        

        super().__init__(video_file=video_file)
    
    def _find_highlight_time(self, file: str) -> list[float]:
        """
        Overrides parent class method, uses the yellow square from the frame
        of the kill to find the highlight time. The elements are separated by
        at least a difference of five (5) seconds.
        """
        video_clip = moviepy.editor.VideoFileClip(file).crop(self._left_crop,
                                                             self._top_crop,
                                                             self._right_crop,
                                                             self._bottom_crop)
        yellow_hsv_lower_bound = np.array([20, 100, 100])
        yellow_hsv_upper_bound = np.array([40, 255, 255])
        minimum_area = 1500
        highlights = []
        time_interval = 0
        while time_interval < video_clip.duration:
            hsv_frame = cv2.cvtColor(video_clip.get_frame(time_interval),
                                     cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv_frame, yellow_hsv_lower_bound,
                               yellow_hsv_upper_bound)
            contours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_NONE)[0]
            for contour in contours:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                # shape should have 4 verticies
                if len(approx) == 4:
                    area = cv2.contourArea(contour)
                    if area > minimum_area:
                        highlights.append(time_interval)
                        time_interval += 4.75
            time_interval += 0.25
        
        return highlights