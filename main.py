import PySimpleGUI as sg
from pytube import YouTube, exceptions, Playlist
from helpers import get_img_data, update_thumbnail_preview, generate_folder
from pathlib import Path
import os


# TODO: Keys to Enums


DEFAULT_DOWNLOAD_PATH = str(Path.home() / 'Downloads')

WINDOW_WIDTH = 150
WINDOW_HEIGHT = 150
margins = (WINDOW_WIDTH, WINDOW_HEIGHT)
DEFAULT_LINK = 'https://www.youtube.com/watch?v=F_rJFbWrK3Y'

url_handler = [[sg.Text('URL: '),
                sg.InputText(DEFAULT_LINK, key='-url-'),
                sg.Button('Submit', enable_events=True, key='-submit_button-')],
               [sg.Button('Upload Batch File (.txt only)', enable_events=True, key='-upload_button-'),
                sg.Button('Delete selection', enable_events=True, disabled=True, key='-delete_selection-'),
                sg.Button('Delete All', enable_events=True, disabled=True, key='-delete_all-')],
               [sg.Listbox(values=[], size=(70, 20), enable_events=True, key='-list-')],
               [sg.Text('Download Location: ', size=(15, 1), auto_size_text=False),
                sg.InputText(DEFAULT_DOWNLOAD_PATH, key='-download_location-'),
                sg.FolderBrowse()],
               [sg.Button('Download All', enable_events=True, disabled=True, key='-download_all-')]]

DEFAULT_IMG = 'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'
img_data = get_img_data(DEFAULT_IMG, first=True)

video_preview = [[sg.Text('Title of the video', size=(30, 2), key='-video_title-')],
                 [sg.Image(data=img_data, key='-video_preview-')]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Audio Batch Downloader', layout=layout, margins=margins, finalize=True)
submit_button = window['-submit_button-']
video_list = window['-list-']
delete_selection = window['-delete_selection-']
delete_all = window['-delete_all-']

download_button = window['-download_all-']
title_list = []
audio_download_list = []
image_list = []

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
            # Update title
            video_title = window['-video_title-']
            title = video.title
            video_title.update(title)

            # Update image
            video_img = window['-video_preview-']
            img_url = video.thumbnail_url
            img_data = get_img_data(img_url)
            video_img.update(data=img_data)
            image_list.append(img_data)

            audio = video.streams.get_audio_only()

            title_list.append(video.title)
            audio_download_list.append(audio)
            video_list.update(values=title_list)
            submit_button.update(disabled=False)
            download_button.update(disabled=False)
            delete_all.update(disabled=False)
            delete_selection.update(disabled=False)

    elif event == '-delete_selection-':
        try:
            index = video_list.Widget.curselection()[0]
        except IndexError:
            print('Did not select anything...')
        else:
            del title_list[index]
            del audio_download_list[index]
            if not title_list:
                delete_all.update(disabled=True)
                delete_selection.update(disabled=True)

            video_list.update(title_list)

    elif event == '-delete_all-':
        title_list = []
        audio_download_list = []
        video_list.update(values=title_list)
        delete_all.update(disabled=True)
        delete_selection.update(disabled=True)

    elif event == '-list-':
        print(event)
        try:
            index = video_list.Widget.curselection()[0]
        except IndexError:
            print('Did not select anything...')
        else:
            video_img.update(data=image_list[index])
            video_title.update(title_list[index])


    elif event == '-download_all-':
        folder_name = generate_folder()
        download_path = os.path.join(values['-download_location-'], folder_name)
        print(download_path)
        for audio in audio_download_list:
            audio.download(download_path)
