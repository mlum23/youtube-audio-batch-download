import PySimpleGUI as sg
from pytube import YouTube, exceptions, Playlist
from helpers import get_img_data, update_thumbnail_preview, generate_folder
from pathlib import Path
import os

DEFAULT_DOWNLOAD_PATH = str(Path.home() / "Downloads")

WINDOW_WIDTH = 150
WINDOW_HEIGHT = 150
margins = (WINDOW_WIDTH, WINDOW_HEIGHT)
DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'

url_handler = [[sg.Text('URL: '),
                sg.InputText(DEFAULT_LINK, key='-url-'),
                sg.Button('Submit', enable_events=True, key='-submit_button-')],
               [sg.Button('Upload Batch File (.txt only)', enable_events=True, key='-upload_button-')],
               [sg.Listbox(values=[], size=(70, 20), key='-list-')],
               [sg.Text('Download Location: ', size=(15, 1), auto_size_text=False),
                sg.InputText(DEFAULT_DOWNLOAD_PATH, key='-download_location-'),
                sg.FolderBrowse()],
               [sg.Button('Download All', enable_events=True, disabled=True, key='-download_all-')]]

DEFAULT_IMG = 'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'
img_data = get_img_data(DEFAULT_IMG, first=True)

video_preview = [[sg.Text('Title of the video', key='-video_title-')],
                 [sg.Image(data=img_data, key='-video_preview-')]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Audio Batch Downloader', layout=layout, margins=margins, finalize=True)
submit_button = window['-submit_button-']
video_list = window['-list-']

download_button = window['-download_all-']
title_list = []
audio_download_list = []

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
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
            window.Element('-list-').update(values=title_list)
            submit_button.update(disabled=False)
            download_button.update(disabled=False)

    elif event == '-select_download_location-':
        print(values)
        sg.PopupGetFolder('Choose folder')

    elif event == '-download_all-':
        folder_name = generate_folder()
        download_path = os.path.join(values['-download_location-'], folder_name)
        print(download_path)
        for audio in audio_download_list:
            audio.download(download_path)
