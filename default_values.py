from enum import Enum
from pathlib import Path


class Window(Enum):
    SIZE = (1350, 950)
    LEFT_MARGIN = 130
    TOP_MARGIN = 80
    MARGIN = (LEFT_MARGIN, TOP_MARGIN)


class Button(Enum):
    SUBMIT = '-submit_button-'
    PLAYLIST_SUBMIT = '-submit_playlist_button-'
    CSV_UPLOAD = '-csv_upload-'
    CSV_SUBMIT = '-csv_submit'
    DELETE_SELECTION = '-delete_selection-'
    DELETE_ALL = '-delete_all-'
    DELETE_ABOVE = '-delete_above-'
    DELETE_BELOW = '-delete_below'
    DOWNLOAD_ALL = '-download_all-'
    DOWNLOAD_LOCATION = '-download_location-'


class Input(Enum):
    CSV_LOCATION = '-csv_location-'
    DOWNLOAD_LOCATION = '-download_location-'
    DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'
    DEFAULT_PLAYLIST = 'https://www.youtube.com/watch?v=2tQRlpNIEEU&list=PLhkTlkgX3j0sxvUCwE8r22Exyj6mxBbWK'
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
    MAX_VALUE = 100


class DownloadSize(Enum):
    DOWNLOAD_SIZE = '-download_size-'


class Font(Enum):
    DEFAULT = ("Helvetica", 12)


class Image(Enum):
    DEFAULT = 'https://static.wixstatic.com/media/71372e_6b4a1c9bd3f446a2842b688626cbc3d0~mv2' \
                                 '.png/v1/fill/w_300%2Ch_300%2Cal_c%2Cq_90/file.jpg'
