import PySimpleGUI as sg
from pytube import YouTube, exceptions, Playlist
from helpers import get_img_data, generate_folder, disable_buttons, update_download_size_message
import os
from default_values import Window, Button, Input, List, Video, ProgBar, DownloadSize, Font


class YouTubeAudioBatchDownloader:
    def __init__(self):
        self.__download_size = 0
        self.__values = None
        self.__event = None
        self.__title_list = []
        self.__audio_download_list = []
        self.__image_list = []
        self.__main_layout = [
            [
                sg.Text('Video URL:', font=Font.DEFAULT.value),
                sg.InputText(Input.DEFAULT_LINK.value, font=Font.DEFAULT.value, key=Input.URL),
                sg.Button('Submit', enable_events=True, font=Font.DEFAULT.value, key=Button.SUBMIT)
            ],
            [
                sg.Text('Playlist URL: ', font=Font.DEFAULT.value),
                sg.InputText(Input.DEFAULT_PLAYLIST.value, font=Font.DEFAULT.value, key=Input.PLAYLIST_URL),
                sg.Button('Submit', enable_events=True, font=Font.DEFAULT.value, key=Button.PLAYLIST_SUBMIT)
            ],
            [
                sg.Button('Upload Batch File (.txt only)', enable_events=True, key=Button.UPLOAD),
                sg.Button('Delete selection', enable_events=True, font=Font.DEFAULT.value,
                          disabled=True, key=Button.DELETE_SELECTION),
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
                sg.FolderBrowse(font=Font.DEFAULT.value)
            ],
            [
                sg.Button('Download All', enable_events=True, disabled=True,
                          font=Font.DEFAULT.value, key=Button.DOWNLOAD_ALL),
                sg.Text('Approx. Download Size: 0 B', size=(40, 1),
                        font=Font.DEFAULT.value, key=DownloadSize.DOWNLOAD_SIZE)
            ],
            [
                sg.ProgressBar(ProgBar.MAX_VALUE.value, orientation='h', size=(20, 20), key=ProgBar.PROGRESS_BAR),
                sg.Button('Cancel Load/Download', font=Font.DEFAULT.value, disabled=True, key='cancel')
            ],
            [
                sg.Text(size=(50, 1), key=Input.CURRENT_DOWNLOAD)
            ]
        ]
        self.__DEFAULT_IMG_URL = 'https://static.wixstatic.com/media/71372e_6b4a1c9bd3f446a2842b688626cbc3d0~mv2' \
                                 '.png/v1/fill/w_300%2Ch_300%2Cal_c%2Cq_90/file.jpg'
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

        self.__delete_all = self.__window[Button.DELETE_ALL]
        self.__submit_button = self.__window[Button.SUBMIT]
        self.__submit_playlist_button = self.__window[Button.PLAYLIST_SUBMIT]
        self.__delete_selection = self.__window[Button.DELETE_SELECTION]
        self.__download_button = self.__window[Button.DOWNLOAD_ALL]
        self.__video_title = self.__window[Video.TITLE]
        self.__video_list = self.__window[List.DOWNLOAD_LIST]
        self.__video_img = self.__window[Video.THUMBNAIL]

    def __update_preview(self, video):
        title = video.title
        self.__video_title.update(title)

        # Update image
        img_url = video.thumbnail_url
        img_data = get_img_data(img_url)
        self.__video_img.update(data=img_data)
        self.__image_list.append(img_data)

    def __update_lists(self, video):
        # Update title
        title = video.title
        self.__video_title.update(title)

        # Update image and title
        self.__update_preview(video)

        audio = video.streams.get_audio_only()
        self.__download_size += audio.filesize
        update_download_size_message(self.__download_size, self.__window)
        self.__title_list.append(video.title)
        self.__audio_download_list.append(audio)
        self.__video_list.Widget.insert(len(self.__title_list) - 1, video.title)

    def __set_to_default(self):
        self.__title_list = []
        self.__audio_download_list = []
        self.__image_list = []
        self.__download_size = 0
        self.__video_list.update(values=self.__title_list)
        disable_buttons(True, self.__delete_all, self.__delete_selection, self.__download_button)
        self.__video_img.update(data=self.__DEFAULT_IMG_DATA)
        self.__video_title.update(self.__DEFAULT_TITLE)
        self.__window[ProgBar.PROGRESS_BAR].update_bar(0)
        update_download_size_message(self.__download_size, self.__window)

    def __message_empty_list(self):
        self.__window[Input.CURRENT_DOWNLOAD].update('Load a video to download')
        disable_buttons(True, self.__download_button)

    def __message_non_empty_list(self):
        self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')

    def __handle_submit_single_video(self):
        disable_buttons(True, self.__submit_button, self.__submit_playlist_button)
        url = self.__values[Input.URL]
        try:
            video = YouTube(url)
        except (exceptions.RegexMatchError, KeyError):
            sg.Popup('Cannot find video', title='Error')

        else:
            self.__update_preview(video)
            self.__update_lists(video)
            disable_buttons(False, self.__download_button, self.__delete_all, self.__delete_selection)

        disable_buttons(False, self.__submit_button, self.__submit_playlist_button)
        self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')

    def __handle_submit_playlist(self):
        disable_buttons(True, self.__download_button, self.__delete_all,
                        self.__delete_selection, self.__submit_button, self.__submit_playlist_button)

        url = self.__values[Input.PLAYLIST_URL]

        try:
            self.__window[Input.CURRENT_DOWNLOAD].update('Initializing...')
            videos = Playlist(url)  # Returns array of URLs

        except (exceptions.RegexMatchError, KeyError):
            sg.Popup('Cannot find video', title='Error')

        else:
            num_videos_found = len(videos)
            current_progress_bar_value = 0
            progress_bar_iterator = ProgBar.MAX_VALUE.value / num_videos_found

            if len(videos) == 0:  # Valid link but not a playlist or no videos found
                sg.Popup('Invalid Playlist')
                self.__window[Input.CURRENT_DOWNLOAD].update('')
            else:
                for link in videos:
                    try:
                        video = YouTube(link)
                        update_text = 'Currently loading: ' + video.title
                        self.__window[Input.CURRENT_DOWNLOAD].update(update_text)
                    except (exceptions.VideoUnavailable,
                            exceptions.VideoPrivate,
                            exceptions.VideoRegionBlocked):
                        continue
                    else:
                        self.__update_lists(video)
                        self.__update_preview(video)
                        update_download_size_message(self.__download_size, self.__window)
                    finally:
                        self.__window[ProgBar.PROGRESS_BAR].update_bar(current_progress_bar_value
                                                                       + progress_bar_iterator)
                        current_progress_bar_value += progress_bar_iterator

                self.__window[Input.CURRENT_DOWNLOAD].update('Ready to download!')

                disable_buttons(False, self.__download_button, self.__delete_all,
                                self.__delete_selection, self.__submit_button, self.__submit_playlist_button)

    def __handle_delete_selection(self):
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
                disable_buttons(True, self.__delete_all, self.__delete_selection)
                self.__video_img.update(data=self.__DEFAULT_IMG_DATA)
                self.__video_title.update(self.__DEFAULT_TITLE)
            else:
                if index == 0:
                    index = 1

                self.__video_img.update(data=self.__image_list[index - 1])
                self.__video_title.update(self.__title_list[index - 1])

            self.__video_list.update(self.__title_list)
            update_download_size_message(self.__download_size, self.__window)

            if self.__title_list:  # Not empty
                self.__message_non_empty_list()
            else:  # Empty list
                self.__message_empty_list()

    def __handle_download_all(self):
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
        while True:
            self.__event, self.__values = self.__window.read()
            if self.__event == sg.WIN_CLOSED:
                break

            elif self.__event == Button.SUBMIT:
                self.__handle_submit_single_video()

            elif self.__event == Button.PLAYLIST_SUBMIT:
                self.__handle_submit_playlist()

            elif self.__event == Button.DELETE_SELECTION:
                self.__handle_delete_selection()

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


if __name__ == '__main__':
    x = YouTubeAudioBatchDownloader()
    x.run()
