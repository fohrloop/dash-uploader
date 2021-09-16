
import uuid
import dash
import dash_uploader as du

from dash import html
from dash.dependencies import Output



app = dash.Dash(__name__)
du.configure_upload(app, 'uploads')

app.layout = html.Div([
    html.Div( 
        du.Upload(
            id='upload', 
            filetypes=['tar', 'zip', 'mzxml', 'mzml'], 
            max_files=10,
            text='Click here for file upload or drag and drop.'),
    ),
    html.Div(id="callback-output"),
])


@du.callback(output=Output('callback-output', 'children'), id='upload')
def output(filenames):
    return html.Ul([html.Li(fn) for fn in filenames])


if __name__ == '__main__':
    app.run_server(debug=True)