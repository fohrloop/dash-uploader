from pathlib import Path

import dash_uploader as du
import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

UPLOAD_FOLDER = r"C:\tmp\Uploads"
du.configure_upload(app, UPLOAD_FOLDER)

app.layout = html.Div(
    [
        html.H1('Demo'),
        html.Div(
            du.Upload(
                text='Drag and Drop files here',
                text_completed='Completed: ',
                pause_button=False,
                cancel_button=True,
                max_file_size=1800,  # 1800 Mb
                filetypes=['zip', 'rar'],
                css_id='upload-files-div',
            ),
            style={
                'textAlign': 'center',
                'width': '600px',
                'padding': '10px',
                'display': 'inline-block'
            },
        ),
        html.Div(id='callback-output')
    ],
    style={
        'textAlign': 'center',
    },
)


@app.callback(
    Output('callback-output', 'children'),
    [Input('upload-files-div', 'isCompleted')],
    [State('upload-files-div', 'fileNames')],
)
def display_files(isCompleted, fileNames):

    if not isCompleted:
        return
    if fileNames is not None:
        out = []
        for filename in fileNames:
            file = Path(UPLOAD_FOLDER) / filename
            out.append(file)
        return html.Ul([html.Li(str(x)) for x in out])
    return html.Ul(html.Li("No Files Uploaded Yet!"))


if __name__ == '__main__':
    app.run_server(debug=True)
