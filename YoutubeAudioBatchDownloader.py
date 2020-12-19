"""
The YoutubeAudioBatchDownloader module contains a class which implements the layout of the GUI,
various event handlers for buttons, input text, and retrieving the media
source from YouTube with the help of pytube.
"""


import PySimpleGUI as sg
from pytube import YouTube, exceptions, Playlist
from helpers import get_img_data, generate_folder, disable_buttons, humansize
import os
from default_values import Window, Button, Input, List, Video, ProgBar, DownloadSize, Font, Image
import csv


class YouTubeAudioBatchDownloader:
    """
    This class implements the layout of the GUI using PySimpleGUI,
    various event handlers for buttons, input text, and retrieving the media
    source from YouTube with pytube.
    """

    def __init__(self):
        """
        Initializes the GUI.

        Contains the initial setup of the GUI (all lists empty, download size set to 0, etc.)
        as well as all the buttons that will be used in the program.
        """
        self.__download_size = 0
        self.__values = None
        self.__event = None
        self.__title_list = []
        self.__audio_download_list = []
        self.__image_list = []
        self.__main_layout = [
            [
                sg.Text('Video URL:', font=Font.DEFAULT.value),
                sg.InputText(font=Font.DEFAULT.value, key=Input.URL),
                sg.Button('Submit', enable_events=True, font=Font.DEFAULT.value, key=Button.SUBMIT)
            ],
            [
                sg.Text('Playlist URL: ', font=Font.DEFAULT.value),
                sg.InputText(font=Font.DEFAULT.value, key=Input.PLAYLIST_URL),
                sg.Button('Submit', enable_events=True, font=Font.DEFAULT.value, key=Button.PLAYLIST_SUBMIT)
            ],
            [
                sg.Text('CSV File:', font=Font.DEFAULT.value),
                sg.InputText(font=Font.DEFAULT.value, key=Input.CSV_LOCATION),
                sg.FileBrowse('Browse',
                              file_types=(('CSV Files', '*.csv'),),
                              enable_events=True,
                              font=Font.DEFAULT.value,
                              key=Button.CSV_UPLOAD),
                sg.Button('Submit',
                          enable_events=True,
                          font=Font.DEFAULT.value,
                          key=Button.CSV_SUBMIT)
            ],
            [
              sg.Button('Delete selection',
                        enable_events=True,
                        font=Font.DEFAULT.value,
                        disabled=True,
                        key=Button.DELETE_SELECTION),
              sg.Button('Delete Everything Above',
                        enable_events=True,
                        font=Font.DEFAULT.value,
                        disabled=True,
                        key=Button.DELETE_ABOVE),

                sg.Button('Delete Everything Below',
                          enable_events=True,
                          disabled=True,
                          font=Font.DEFAULT.value,
                          key=Button.DELETE_BELOW),

                sg.Button('Delete All',
                          enable_events=True,
                          disabled=True,
                          font=Font.DEFAULT.value,
                          key=Button.DELETE_ALL)
            ],
            [
                sg.Listbox(values=[], size=(70, 20), font=Font.DEFAULT.value,
                           enable_events=True, no_scrollbar=False, key=List.DOWNLOAD_LIST)
            ],
            [
                sg.Text('Download Location: ', size=(15, 1), font=Font.DEFAULT.value, auto_size_text=False),
                sg.InputText(Input.DEFAULT_DOWNLOAD_PATH.value, font=Font.DEFAULT.value, key=Input.DOWNLOAD_LOCATION),
                sg.FolderBrowse(font=Font.DEFAULT.value, key=Button.DOWNLOAD_LOCATION)
            ],
            [
                sg.Button('Download All', enable_events=True, disabled=True,
                          font=Font.DEFAULT.value, key=Button.DOWNLOAD_ALL),
                sg.Text('Approx. Download Size: 0 B', size=(40, 1),
                        font=Font.DEFAULT.value, key=DownloadSize.DOWNLOAD_SIZE)
            ],
            [
                sg.ProgressBar(ProgBar.MAX_VALUE.value, orientation='h', size=(20, 20), key=ProgBar.PROGRESS_BAR),
            ],
            [
                sg.Text(size=(50, 1), key=Input.CURRENT_DOWNLOAD)
            ]
        ]
        self.__DEFAULT_IMG_URL = Image.DEFAULT.value
        self.__DEFAULT_TITLE = 'Title of the video'
        self.__DEFAULT_IMG_DATA = get_img_data(self.__DEFAULT_IMG_URL, first=True)
        self.__video_preview = [[sg.Text(self.__DEFAULT_TITLE, size=(40, 2),
                                         font=("Helvetica", 14), key=Video.TITLE)],
                                [sg.Image(data=self.__DEFAULT_IMG_DATA, key=Video.THUMBNAIL)]]

        self.__layout = [[sg.Text(f'{" " * 20}YouTube Audio Batch Downloader', font=("Helvetica", 32), pad=(1, 20))],
                         [sg.Column(self.__main_layout),
                          sg.VSeparator(),
                          sg.Column(self.__video_preview)]]

        self.__window = sg.Window(title='YouTube Audio Batch Downloader',
                                  size=Window.SIZE.value,
                                  layout=self.__layout,
                                  margins=Window.MARGIN.value,
                                  finalize=True)

        # Delete buttons
        self.__delete_all = self.__window[Button.DELETE_ALL]
        self.__delete_selection = self.__window[Button.DELETE_SELECTION]
        self.__delete_above = self.__window[Button.DELETE_ABOVE]
        self.__delete_below = self.__window[Button.DELETE_BELOW]

        # Upload buttons
        self.__submit_button = self.__window[Button.SUBMIT]
        self.__csv_submit_button = self.__window[Button.CSV_SUBMIT]
        self.__csv_browse_button = self.__window[Button.CSV_UPLOAD]
        self.__submit_playlist_button = self.__window[Button.PLAYLIST_SUBMIT]

        # Download related buttons
        self.__download_button = self.__window[Button.DOWNLOAD_ALL]
        self.__download_location_button = self.__window[Button.DOWNLOAD_LOCATION]

        # Preview screen
        self.__video_title = self.__window[Video.TITLE]
        self.__video_list = self.__window[List.DOWNLOAD_LIST]
        self.__video_img = self.__window[Video.THUMBNAIL]

    def __update_preview(self, video):
        """
        Updates the preview thumbnail and title of the video.

        This method also saves the thumbnail into the image_list array.

        :param video: a pytube.YouTube object
        """
        # Update title
        title = video.title
        self.__video_title.update(title)

        # Update image
        img_url = video.thumbnail_url
        img_data = get_img_data(img_url)
        self.__video_img.update(data=img_data)
        self.__image_list.append(img_data)

    def __update_lists(self, video):
        """
        Updates the title_list, audio_download_list, and image_list (via update_preview)
        arrays when a video is submitted to load.

        :param video: a pytube.Youtube object
        """
        # Update image and title
        self.__update_preview(video)

        audio = video.streams.get_audio_only()
        self.__download_size += audio.filesize
        self.__update_download_size_message()
        self.__title_list.append(video.title)
        self.__audio_download_list.append(audio)
        self.__video_list.Widget.insert(len(self.__title_list) - 1, video.title)

    def __update_list_of_videos(self):
        """
        Updates the GUI's list of videos with the values in title_list
        """
        self.__video_list.update(values=self.__title_list)

    def __update_download_size_message(self):
        """
        Updates the download size text.
        """
        self.__window[DownloadSize.DOWNLOAD_SIZE]\
            .update(f'Approx. Download Size: {humansize(self.__download_size)}')

    def __disable_all_buttons(self, disabled):
        """
        Sets all buttons in the GUI to whatever value disabled is.

        :param disabled: a boolean, True/False
        """
        self.__disable_delete_buttons(disabled)
        self.__disable_upload_buttons(disabled)

    def __disable_upload_buttons(self, disabled):
        """
        Disables all buttons in the GUI that submits a video for download.

        These buttons include:
            - csv_submit_button
            - csv_browse_button
            - submit_button
            - submit_playlist_button
            - download_location_button
            - download_button
        :param disabled: a boolean, True/False
        """
        disable_buttons(disabled, self.__submit_button, self.__csv_submit_button, self.__download_location_button,
                        self.__csv_browse_button, self.__submit_playlist_button, self.__download_button)

    def __disable_delete_buttons(self, disabled):
        """
        Disables the delete buttons in the GUI.

        These buttons include:
            - delete_all
            - delete_selection
            - delete_above
            - delete_below

        :param disabled: a boolean, True/False
        """
        disable_buttons(disabled, self.__delete_all, self.__delete_selection,
                        self.__delete_above, self.__delete_below)

    def __set_to_default(self):
        """
        Sets all settings back to the initial settings
        (all arrays empty, download size set to 0, etc.)
        """
        self.__title_list = []
        self.__audio_download_list = []
        self.__image_list = []
        self.__download_size = 0
        self.__update_list_of_videos()
        self.__disable_delete_buttons(True)
        self.__video_img.update(data=self.__DEFAULT_IMG_DATA)
        self.__video_title.update(self.__DEFAULT_TITLE)
        self.__window[ProgBar.PROGRESS_BAR].update_bar(0)
        self.__update_download_size_message()

    def __message_empty_list(self):
        """
        Displays an appropriate message when the GUI
        displays no videos in the list.
        """
        self.__window[Input.CURRENT_DOWNLOAD].update('Load a video to download')
        disable_buttons(True, self.__download_button)

    def __message_non_empty_list(self):
        """
        Displays an appropriate message when the video list
        in the GUI is not empty.
        """
        self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')

    def __upload_single_video(self, video_url, multi_upload=False):
        """
        Loads the YouTube video from link.

        This method gets the YouTube video using pytube, then internally updates the
        title_list, image_list, and audio_list using the update_lists method.

        :param video_url: the URL of the YouTube video, as a string.
        :param multi_upload: False if this method is only being called once (ie: single upload)
                             True if this method is being used for loading multiple videos
                             (such as playlists and csv file).
        """
        self.__disable_upload_buttons(True)
        try:
            video = YouTube(video_url)
            update_text = 'Currently loading: ' + video.title
            self.__window[Input.CURRENT_DOWNLOAD].update(update_text)
        except (exceptions.VideoUnavailable,
                exceptions.VideoPrivate,
                exceptions.VideoRegionBlocked,
                exceptions.RegexMatchError):
            pass
        else:
            self.__update_lists(video)
            self.__update_download_size_message()
        finally:
            if len(self.__title_list) > 0 and not multi_upload:  # Edge case where no videos and wrong link
                self.__disable_delete_buttons(False)
            self.__disable_upload_buttons(False)

        if not multi_upload:
            self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')

    def __upload_multi_video(self, array_of_video_urls):
        """
        Loads multiple YouTube videos.

        This method is called when handling playlists and csv files.
        :param array_of_video_urls: an array of URLs of YouTube videos, as a string.
        """
        self.__disable_all_buttons(True)
        num_videos = len(array_of_video_urls)
        if num_videos == 0:
            sg.Popup('Invalid playlist')
            self.__disable_upload_buttons(False)
            if len(self.__title_list) > 0:
                self.__disable_delete_buttons(False)
            return
        current_progress_bar_value = 0

        progress_bar_iterator = ProgBar.MAX_VALUE.value / num_videos
        for link in array_of_video_urls:
            self.__upload_single_video(link, multi_upload=True)

            self.__window[ProgBar.PROGRESS_BAR].update_bar(current_progress_bar_value
                                                           + progress_bar_iterator)
            current_progress_bar_value += progress_bar_iterator

        self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')
        self.__disable_all_buttons(False)

    def __handle_csv_upload(self):
        """
        Handles the event for the CSV upload button.
        """
        csv_file = self.__values[Input.CSV_LOCATION]
        if not csv_file.lower().endswith('.csv'):
            sg.Popup('Invalid CSV file')
            return
        try:
            with open(csv_file, 'r') as file:
                data = list(csv.reader(file))
                data = [link[0] for link in data]
                self.__upload_multi_video(data)
        except FileNotFoundError:
            sg.Popup('Unable to find file.')

    def __handle_submit_single_video(self):
        """
        Handles the event for submitting a single video URL.
        """
        url = self.__values[Input.URL]
        self.__upload_single_video(url)

    def __handle_submit_playlist(self):
        """
        Handles the event for submitting a playlist.
        """
        url = self.__values[Input.PLAYLIST_URL]

        try:
            videos = Playlist(url)  # Returns array of URLs

        except (exceptions.RegexMatchError, KeyError):
            sg.Popup('Cannot find playlist', title='Error')
            self.__window[Input.CURRENT_DOWNLOAD].update('')
            return
        else:
            self.__upload_multi_video(videos)

    def __handle_delete_selection(self):
        """
        Deletes the selected video in the video list of the GUI.

        This also removes the info of the video from title_list, image_list,
        and audio_download_list, as well as updates the download size.
        """
        try:
            index = self.__video_list.Widget.curselection()[0]
        except IndexError:
            pass
        else:
            self.__download_size -= self.__audio_download_list[index].filesize
            del self.__title_list[index]
            del self.__audio_download_list[index]
            del self.__image_list[index]

            if not self.__title_list:
                self.__disable_delete_buttons(True)
                self.__video_img.update(data=self.__DEFAULT_IMG_DATA)
                self.__video_title.update(self.__DEFAULT_TITLE)
            else:
                if index == 0:
                    index = 1

                self.__video_img.update(data=self.__image_list[index - 1])
                self.__video_title.update(self.__title_list[index - 1])

            self.__update_list_of_videos()
            self.__update_download_size_message()

            if self.__title_list:  # Not empty
                self.__message_non_empty_list()
            else:  # Empty list
                self.__message_empty_list()

    def __handle_delete_above(self):
        """
        Deletes all videos above the selected index in the GUI video list.

        This method also removes the info of the video from title_list, image_list,
        and audio_download_list, as well as updates the download size.
        :return:
        """
        try:
            index = self.__video_list.Widget.curselection()[0]
        except IndexError:
            pass
        else:
            if len(self.__title_list) < 2:
                return

            if index == 0:
                return

            for i in range(index):
                self.__download_size -= self.__audio_download_list[i].filesize

            self.__title_list = self.__title_list[index:]
            self.__audio_download_list = self.__audio_download_list[index:]
            self.__image_list = self.__image_list[index:]

            self.__update_download_size_message()
            self.__update_list_of_videos()

    def __handle_delete_below(self):
        """
        Deletes all videos above the selected index in the GUI video list.

        This also removes the info of the video from title_list, image_list,
        and audio_download_list, as well as updates the download size.
        """
        try:
            index = self.__video_list.Widget.curselection()[0]
        except IndexError:
            pass
        else:
            if len(self.__title_list) < 2:
                return

            if index == len(self.__title_list) - 1:
                return

            for i in range(index + 1, len(self.__title_list)):
                self.__download_size -= self.__audio_download_list[i].filesize

            self.__title_list = self.__title_list[:index + 1]
            self.__audio_download_list = self.__audio_download_list[:index + 1]
            self.__image_list = self.__image_list[:index + 1]

            self.__update_download_size_message()
            self.__update_list_of_videos()

    def __handle_download_all(self):
        """
        Downloads all videos in the GUI video list to file location.

        This method creates a folder in the download location with all
        the audio files in the video list.

        The folder is in the format Youtube_Audio_Batch_Downloader_MM_DD_YYYY_hh_mm_ss
        """
        folder_name = generate_folder()
        download_path = os.path.join(self.__values[Input.DOWNLOAD_LOCATION], folder_name)
        num_videos = len(self.__title_list)
        current_progress_bar = 0
        progress_bar_iterator = ProgBar.MAX_VALUE.value / num_videos
        self.__window[Input.CURRENT_DOWNLOAD].update('Downloading: ')
        for i in range(len(self.__audio_download_list)):
            self.__window[Input.CURRENT_DOWNLOAD].update(f'Downloading: {self.__audio_download_list[i].title} ')
            self.__audio_download_list[i].download(download_path)
            self.__video_img.update(data=self.__image_list[i])
            self.__video_title.update(self.__title_list[i])
            self.__window[ProgBar.PROGRESS_BAR].update_bar(current_progress_bar + progress_bar_iterator)
            current_progress_bar += progress_bar_iterator
        self.__window[Input.CURRENT_DOWNLOAD].update('Download completed!')

    def run(self):
        """
        Runs the event loop of PySimpleGUI.

        This is what drives the program (ie: displays the GUI)
        """
        while True:
            self.__event, self.__values = self.__window.read()

            if self.__event == sg.WIN_CLOSED:
                break

            elif self.__event == Button.CSV_SUBMIT:
                self.__handle_csv_upload()

            elif self.__event == Button.SUBMIT:
                self.__handle_submit_single_video()

            elif self.__event == Button.PLAYLIST_SUBMIT:
                self.__handle_submit_playlist()

            elif self.__event == Button.DELETE_SELECTION:
                self.__handle_delete_selection()

            elif self.__event == Button.DELETE_ABOVE:
                self.__handle_delete_above()

            elif self.__event == Button.DELETE_BELOW:
                self.__handle_delete_below()

            elif self.__event == Button.DELETE_ALL:
                self.__set_to_default()
                self.__message_empty_list()

            elif self.__event == List.DOWNLOAD_LIST:
                try:
                    index = self.__video_list.Widget.curselection()[0]

                except IndexError:
                    continue
                else:
                    self.__video_img.update(data=self.__image_list[index])
                    self.__video_title.update(self.__title_list[index])

            elif self.__event == Button.DOWNLOAD_ALL:
                self.__handle_download_all()