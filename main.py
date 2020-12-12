import PySimpleGUI as sg
from pytube import YouTube, exceptions
import requests
from helpers import get_img_data

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 200
margins = (WINDOW_WIDTH, WINDOW_HEIGHT)
DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'
url_handler = [[sg.Text('URL: '),
                sg.InputText(DEFAULT_LINK, key='-url-'),
                sg.Button('Submit', enable_events=True, key='-submit_button-')]]

DEFAULT_IMG = 'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'
img_data = get_img_data(DEFAULT_IMG, first=True)

video_preview = [[sg.Image(data=img_data, key='-video_preview-')]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Downloader', layout=layout, margins=margins, finalize=True)

submit_button = window['-submit_button-']
thumbnail_preview = window['-video_preview-']

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        print('bye')
        break
    elif event == '-submit_button-':
        submit_button.update(disabled=True)
        url = values['-url-']
        try:
            video = YouTube(url)
        except exceptions.RegexMatchError:
            print('bad link')
        else:
            title = video.title
            # Update thumbnail preview
            img_url = video.thumbnail_url
            img_data = get_img_data(img_url)
            thumbnail_preview.update(data=img_data)
            print(video.title)
            thumbnail_preview.update()
            submit_button.update(disabled=False)

