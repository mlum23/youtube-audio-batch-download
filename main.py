import PySimpleGUI as sg
from pytube import YouTube, exceptions
from helpers import get_img_data, update_thumbnail_preview, get_download_path
import datetime


WINDOW_WIDTH = 150
WINDOW_HEIGHT = 150
margins = (WINDOW_WIDTH, WINDOW_HEIGHT)
DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'
url_handler = [[sg.Text('URL: '),
                sg.InputText(DEFAULT_LINK, key='-url-'),
                sg.Button('Submit', enable_events=True, key='-submit_button-')],
               [sg.Listbox(values=[], size=(60, 20), key='-list-')],
               [sg.Button('Download All', enable_events=True, key='-download_all-')]]

DEFAULT_IMG = 'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'
img_data = get_img_data(DEFAULT_IMG, first=True)

video_preview = [[sg.Text('Title of the video', key='-video_title-')],
                 [sg.Image(data=img_data, key='-video_preview-')]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Downloader', layout=layout, margins=margins, finalize=True)
submit_button = window['-submit_button-']
video_list = window['-list-']
title_list = []
audio_download_list = []

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
            # Update video
            update_thumbnail_preview(window, video)
            audio = video.streams.get_audio_only()
            title_list.append(video.title)
            audio_download_list.append(audio)
            print(title_list)
            print(audio)
            window.Element('-list-').update(values=title_list)
            submit_button.update(disabled=False)
    elif event == '-download_all-':
        download_path = get_download_path()
        for audio in audio_download_list:
            audio.download(download_path)




