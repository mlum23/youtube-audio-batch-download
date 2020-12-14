from enum import Enum
from pathlib import Path


class Window(Enum):
    WIDTH = 150
    HEIGHT = 150
    MARGIN = (WIDTH, HEIGHT)


class Button(Enum):
    SUBMIT = '-submit_button-'
    PLAYLIST_SUBMIT = '-submit_playlist_button-'
    UPLOAD = '-upload_button-'
    DELETE_SELECTION = '-delete_selection-'
    DELETE_ALL = '-delete_all-'
    DOWNLOAD_ALL = '-download_all-'


class Input(Enum):
    DOWNLOAD_LOCATION = '-download_location-'
    DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'
    DEFAULT_PLAYLIST = 'https://www.youtube.com/watch?v=RUQl6YcMalg&list=PLDIoUOhQQPlXr63I_vwF9GD8sAKh77dWU'
    DEFAULT_DOWNLOAD_PATH = str(Path.home() / 'Downloads')
    URL = '-url-'
    PLAYLIST_URL = '-playlist_url-'
    CURRENT_DOWNLOAD = '-current_download-'


class List(Enum):
    DOWNLOAD_LIST = '-download_list-'


class Video(Enum):
    TITLE = '-video_title-'
    THUMBNAIL = '-video_thumbnail-'


class ProgBar(Enum):
    PROGRESS_BAR = '-prog_bar-'

