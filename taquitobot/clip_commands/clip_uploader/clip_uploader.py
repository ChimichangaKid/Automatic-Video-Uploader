"""
clip_uploader.py

Class implementation to handle uploading clips to YouTube that have been
edited by the clip_editor.

Attributes:

TODO:

Versioning:
    Author: Aidan (Chimichanga Kid)
    Date: 2024-08-23
    Version: 1.0.0

Notes:

"""

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .upload_keys import COOKIES_FOLDER, DESCRIPTION_TEMPLATE

chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={COOKIES_FOLDER}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


class YouTubeUploader:
    def __init__(self, video_title: str, game_title: str) -> None:
        self._driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self._video_title = (
            (video_title
            + f" #{game_title} #{game_title}Clip #{game_title}Guides")[:100]
        )
        self._description = DESCRIPTION_TEMPLATE.replace("placeholder", game_title)[
            :5000
        ]

    def upload_to_youtube(self, file_name: Path) -> str:
        """
        Uploads the specified video to YouTube by navigating to site and
        uploading to the logged in user.

        Args:
            file_name (str): The path to the video file that should be
                uploaded.
        Returns:
            (str): The url of the video on YouTube.
        """
        self._driver.get("https://www.youtube.com")
        self._driver.implicitly_wait(5)

        self._go_to_video_manager()
        self._driver.implicitly_wait(5)
        self._upload_video_file_helper(file_name)
        self._driver.implicitly_wait(5)
        self._add_title_and_description()
        self._driver.implicitly_wait(7)
        self._make_public()

        print("Getting link")
        link_element = self._driver.find_element(
            By.XPATH, """//a[contains(@class, "style-scope ytcp-video-info")]"""
        )
        video_link = link_element.get_attribute("href")
        print(f"link is {video_link}")

        time.sleep(3)
        publish_button = self._driver.find_element(
            By.XPATH, '//ytcp-button[@id="done-button"]'
        )
        publish_button.click()

        time.sleep(5)

        try:
            publish_anyways = self._driver.find_element(
                By.XPATH, "//button[.//div[text()='Publish anyway']]"
            )
            publish_anyways.click()
        except NoSuchElementException:
            print("No publish anyways")

        time.sleep(2)

        self._driver.implicitly_wait(7)
        self._driver.quit()

        return video_link

    def _go_to_video_manager(self) -> None:
        """
        Helper method to navigate to video manager screen on YouTube.
        """
        upload_button = self._driver.find_element(
            By.XPATH, """//button[@aria-label="Create"]"""
        )
        upload_button.click()

        self._driver.implicitly_wait(5)

        video_manager_button = self._driver.find_element(
            By.XPATH,
            """//tp-yt-paper-item[.//yt-formatted-string[contains(., "Upload video")]]""",
        )
        video_manager_button.click()

        return

    def _upload_video_file_helper(self, video_path: Path) -> None:
        """
        Helper method to upload the specified video to YouTube.

        Args:
            video_path (str): The path to the video file.
        """
        file_input_box = self._driver.find_element(
            By.XPATH, """//input[@type="file"]"""
        )
        file_input_box.send_keys(str(video_path.resolve()))

    def _add_title_and_description(self) -> None:
        """
        Helper method to add the title and description to the video.
        """
        title_textbox = self._driver.find_element(
            By.XPATH,
            """//div[@id="textbox" and contains(@class, "ytcp-social-suggestions-textbox")]""",
        )
        title_textbox.clear()
        time.sleep(0.5)
        title_textbox.send_keys(self._video_title)

        self._driver.implicitly_wait(3)

        description_textbox = self._driver.find_element(
            By.XPATH,
            """//div[@aria-label="Tell viewers about your video (type @ to mention a channel)"]""",
        )
        description_textbox.clear()
        time.sleep(0.5)
        description_textbox.send_keys(self._description)

        self._driver.implicitly_wait(3)

        not_made_for_kids_button = self._driver.find_element(
            By.XPATH,
            """//tp-yt-paper-radio-button[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]""",
        )
        not_made_for_kids_button.click()

        return

    def _make_public(self) -> None:
        """
        Helper method to make the video public.
        """
        next_button = self._driver.find_element(
            By.XPATH, """//ytcp-button[@id="next-button"]"""
        )
        next_button.click()
        self._driver.implicitly_wait(2)
        next_button.click()
        self._driver.implicitly_wait(2)
        next_button.click()
        self._driver.implicitly_wait(2)
        time.sleep(5)

        public_button = self._driver.find_element(
            By.XPATH, """//tp-yt-paper-radio-button[@name="PUBLIC"]"""
        )
        public_button.click()
        time.sleep(15)
        return
