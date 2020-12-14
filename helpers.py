import io
from PIL import Image, ImageTk
import requests
import datetime

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


def generate_folder():
    date_time = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
    name = f'Youtube_Audio_Batch_Downloader_{date_time}'
    return name
