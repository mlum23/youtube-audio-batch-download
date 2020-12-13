import io
from PIL import Image, ImageTk
import requests
from winreg import *

def get_img_data(img_url, maxsize=(150, 150), first=False):
    response = requests.get(img_url, stream=True)
    img = Image.open(response.raw)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def update_thumbnail_preview(window, video):
    # Update title
    video_title = window['-video_title-']
    title = video.title
    video_title.update(title)

    # Update image
    video_img = window['-video_preview-']
    img_url = video.thumbnail_url
    img_data = get_img_data(img_url)
    video_img.update(data=img_data)


def get_download_path():
    with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
        download_path = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

    return download_path
