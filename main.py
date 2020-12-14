import PySimpleGUI as sg
from pytube import YouTube, exceptions, Playlist
import pytube
from helpers import get_img_data, update_thumbnail_preview, generate_folder
import os
from keys import Window, Button, Input, List, Video


url_handler = [
    [
        sg.Text('URL: '),
        sg.InputText(Input.DEFAULT_LINK.value, key=Input.URL),
        sg.Button('Submit', enable_events=True, key=Button.SUBMIT)
    ],
    [
        sg.Text('Playlist URL: '),
        sg.InputText(Input.DEFAULT_PLAYLIST.value, key=Input.PLAYLIST_URL),
        sg.Button('Submit', enable_events=True, key=Button.PLAYLIST_SUBMIT)
    ],
    [
        sg.Button('Upload Batch File (.txt only)', enable_events=True, key=Button.UPLOAD),
        sg.Button('Delete selection', enable_events=True, disabled=True, key=Button.DELETE_SELECTION),
        sg.Button('Delete All', enable_events=True, disabled=True, key=Button.DELETE_ALL)
    ],
    [
        sg.Listbox(values=[], size=(70, 20), enable_events=True, key=List.DOWNLOAD_LIST)
    ],
    [
        sg.Text('Download Location: ', size=(15, 1), auto_size_text=False),
        sg.InputText(Input.DEFAULT_DOWNLOAD_PATH.value, key=Input.DOWNLOAD_LOCATION),
        sg.FolderBrowse()
    ],
    [
        sg.Button('Download All', enable_events=True, disabled=True, key=Button.DOWNLOAD_ALL)
    ]
]

DEFAULT_IMG_URL = 'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'
DEFAULT_TITLE = 'Title of the video'
DEFAULT_IMG_DATA = get_img_data(DEFAULT_IMG_URL, first=True)

video_preview = [[sg.Text(DEFAULT_TITLE, size=(30, 2), key=Video.TITLE)],
                 [sg.Image(data=DEFAULT_IMG_DATA, key=Video.THUMBNAIL)]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Audio Batch Downloader', layout=layout, margins=Window.MARGIN.value, finalize=True)

# Get video Elements
video_list = window[List.DOWNLOAD_LIST]
video_img = window[Video.THUMBNAIL]

# Get all Button Elements
delete_all = window[Button.DELETE_ALL]
submit_button = window[Button.SUBMIT]
submit_playlist_button = window[Button.PLAYLIST_SUBMIT]
delete_selection = window[Button.DELETE_SELECTION]
download_button = window[Button.DOWNLOAD_ALL]
video_title = window[Video.TITLE]

# Initialize arrays
title_list = []
audio_download_list = []
image_list = []

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    elif event == Button.SUBMIT:
        submit_button.update(disabled=True)
        url = values[Input.URL]
        try:
            video = YouTube(url)
        except (exceptions.RegexMatchError, KeyError):
            sg.Popup('Cannot find video', title='Error')

        else:
            # Update title
            title = video.title
            video_title.update(title)

            # Update image
            img_url = video.thumbnail_url
            img_data = get_img_data(img_url)
            video_img.update(data=img_data)
            image_list.append(img_data)

            audio = video.streams.get_audio_only()

            title_list.append(video.title)
            audio_download_list.append(audio)
            video_list.update(values=title_list)

            download_button.update(disabled=False)
            delete_all.update(disabled=False)
            delete_selection.update(disabled=False)

        submit_button.update(disabled=False)

    elif event == Button.PLAYLIST_SUBMIT:
        # submit_playlist_button.update(disabled=True)
        url = values[Input.PLAYLIST_URL]
        try:
            videos = Playlist(url)  # Returns array of URLs
        except (exceptions.RegexMatchError, KeyError):
            sg.Popup('Cannot find video', title='Error')

        else:
            for link in videos:
                print(link)
                try:
                    video = YouTube(link)
                except (exceptions.VideoUnavailable,
                        exceptions.VideoPrivate,
                        exceptions.VideoRegionBlocked):
                    continue
                else:
                    title_list.append(video.title)
                    audio_download_list.append(video.streams.get_audio_only())

                    img_url = video.thumbnail_url
                    img_data = get_img_data(img_url)
                    video_img.update(data=img_data)
                    image_list.append(img_data)

            video_list.update(values=title_list)
            video_img.update(data=image_list[0])
            video_title.update(title_list[0])

            download_button.update(disabled=False)
            delete_all.update(disabled=False)
            delete_selection.update(disabled=False)

    elif event == Button.DELETE_SELECTION:
        try:
            index = video_list.Widget.curselection()[0]
        except IndexError:
            continue
        else:
            del title_list[index]
            del audio_download_list[index]
            del image_list[index]

            if not title_list:
                delete_all.update(disabled=True)
                delete_selection.update(disabled=True)
                video_img.update(data=DEFAULT_IMG_DATA)
                video_title.update(DEFAULT_TITLE)
            else:
                if index == 0:
                    index = 1
                video_img.update(data=image_list[index - 1])
                video_title.update(title_list[index - 1])

            video_list.update(title_list)

    elif event == Button.DELETE_ALL:
        title_list = []
        audio_download_list = []
        image_list = []
        video_list.update(values=title_list)
        delete_all.update(disabled=True)
        delete_selection.update(disabled=True)
        video_img.update(data=DEFAULT_IMG_DATA)
        video_title.update(DEFAULT_TITLE)

    elif event == List.DOWNLOAD_LIST:
        try:
            index = video_list.Widget.curselection()[0]
        except IndexError:
            continue
        else:
            video_img.update(data=image_list[index])
            video_title.update(title_list[index])

    elif event == Button.DOWNLOAD_ALL:
        folder_name = generate_folder()
        download_path = os.path.join(values[Input.DOWNLOAD_LOCATION], folder_name)
        print(download_path)
        for audio in audio_download_list:
            audio.download(download_path)
