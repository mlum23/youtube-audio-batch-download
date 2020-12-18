"""
This module contains various helper functions for the
YoutubeAudioBatchDownloader module.
"""


import io
from PIL import Image, ImageTk
import requests
import datetime
from default_values import DownloadSize


def get_img_data(img_url, first=False):
    """
    Returns the image data.

    :param img_url: the URL of the image, as a string.
    :param first: False if at least one event occured in the PySimpleGUI event loop.
                  True otherwise.
    :return: the image data, as an ImageTk.PhotoImage object
    """
    maxsize = (500, 500)
    response = requests.get(img_url, stream=True)
    img = Image.open(response.raw)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def generate_folder():
    """
    Returns the name of the download folder with all the files.
    :return: the name of the download folder with all the files, as a string.
    """
    date_time = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
    name = f'Youtube_Audio_Batch_Downloader_{date_time}'
    return name


def disable_buttons(is_disabled, *args):
    """
    Disables the button based on is_disabled.

    :param is_disabled: a boolean, True/False
    :param args: an array of PySimpleGui.Button's
    """
    for button in args:
        button.update(disabled=is_disabled)


def humansize(nbytes):
    """
    Returns the converted bytes to a more readable number.

    Source: https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    :param nbytes: the number of bytes, as an integer.
    :return: the converted bytes, as a string.
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
