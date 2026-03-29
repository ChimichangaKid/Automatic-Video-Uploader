"""
clip_editor.py

Implementation for editing the clip with the specified audio and video file, as
well as syncing to the highlight depending on the game.

Attributes:

TODO:

Versioning:
    Author: Aidan (Chimichanga Kid)
    Date: 2024-08-23
    Version 1.0.0

Notes:

"""
import os
import moviepy.editor

class ClipEditor:
    """
    A ClipEditor is a class to handle editing and saving the video footage that
    has been prepared by the ClipPrep object.

    Attributes:

    """
    """
    Private Attributes:
        _clip_prep (ClipPrepAbstract): The clip prep object that contains
            information about how the clip should be edited.
        _horizontal_crop (int): The amount to crop horizontally for the video
            in order to change the aspect ratio in pixels.
    """

    def __init__(self, clip_prep: ClipPrepAbstract") -> None:
        self._clip_prep = clip_prep
        self._horizontal_crop = 270


    def edit_and_save_video(self, clip_file: str, game_title: str,
                            video_title: str) -> str:
        """
        Method to edit and save the video clip to the device at the root of
        the directory. Returns the path to the edited clip.

        Args:
            clip_file (str): The path to the clip that is being edited.
            game_title (str): The title of the game as a string.
            video_title (str): The title of the video set by the user as a
                string.
        Returns:
            (str): The path to the file as a string.
        """
        if game_title == "LethalCompany":
            edited_clip = self._edit_clip(clip_file=clip_file, audio=False)
        else:
            edited_clip = self._edit_clip(clip_file=clip_file, audio=True)
        file_name = video_title + " " + game_title + " tiktok_youtube_shorts.mp4"

        try:
            edited_clip.write_videofile(filename=file_name,
                                        fps=30,
                                        codec="libx264",
                                        preset="superfast",
                                        logger=None)
        except NameError:
            print("Video has not been processed")
            return ""

        return file_name

    def _edit_clip(self, clip_file: str, audio: bool) -> moviepy.editor.VideoFileClip:
        """
        Helper method to handle all the editing for the clip.

        Args:
            clip_file (str): The path to the clip that is being edited.
        Returns:
        """
        video_clip = moviepy.editor.VideoFileClip(clip_file)
        audio_clip = moviepy.editor.AudioFileClip(self._clip_prep._song_name)
        audio_start_time = self._clip_prep._song_start_time - \
                           self._clip_prep._highlight_time[0]
        audio_subclip = audio_clip.subclip(audio_start_time,
                            int(video_clip.duration + audio_start_time))
        if audio:
            edited_clip = video_clip.set_audio(audio_subclip)
        else:
            edited_clip = video_clip
        edited_clip = edited_clip.resize(height=960, width=540)
        centre = int(edited_clip.w / 2)
        edited_clip = edited_clip.crop(x1=centre - self._horizontal_crop,
                                       y1=0,
                                       x2=centre + self._horizontal_crop,
                                       y2=960)

        if self._clip_prep._facecam_clip != "":
            clip_duration = edited_clip.duration
            face_cam_time = self._clip_prep._highlight_time[-1] - \
                            self._clip_prep._face_cam_start_time
            face_cam_clip = moviepy.editor.VideoFileClip(
                            self._clip_prep._facecam_clip)
            face_cam_clip = face_cam_clip.set_start(face_cam_time).crossfadein(1)
            face_cam_clip = face_cam_clip.set_position(("center", "top"))
            edited_clip = moviepy.editor.CompositeVideoClip(
                [edited_clip, face_cam_clip]
            ).set_end(clip_duration)

        return edited_clip

    def remove_footage(self, clip: str) -> bool:
        """
        Helper method to handle removing the old unedited video.

        Args:
            clip (str): Path to the file to be removed as a string.
        Returns:
            (bool): True if the file was there and was removed, False
                otherwise.
        """
        if os.path.exists(clip):
            os.remove(clip)
            return True
        return False
