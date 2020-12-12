import PySimpleGUI as sg
from pytube import YouTube

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 200
margins = (WINDOW_WIDTH, WINDOW_HEIGHT)

url_handler = [[sg.Text('URL: '), sg.InputText(enable_events=True, key='-url-')],
               [sg.Button('Submit', enable_events=True, key='-submit_button-')]]

video_preview = [
    [sg.Graph(
        canvas_size=(250, 250),
        graph_bottom_left=(0, 0),
        graph_top_right=(250, 250),
        key='-video_preview-'
    )]]

layout = [[sg.Column(url_handler),
           sg.VSeparator(),
           sg.Column(video_preview)]]

window = sg.Window(title='Youtube Downloader', layout=layout, margins=margins, finalize=True)
graph = window.Element('-video_preview-')
graph.DrawRectangle((25, 25), (200, 200), line_color='red')

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break


