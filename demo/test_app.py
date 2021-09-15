
import dash
from dash import html

from dash.dependencies import Input, Output, State

import dash_uploader as du


app = dash.Dash(__name__)

du.configure_upload(app, 'uploads')


app.layout = html.Div([

     html.Div( 
         du.Upload(id='upload', 
            filetypes=['tar', 'zip', 'mzXML', 'mzML', 'mzml', 'mzxml'], 
            max_files=10000,
            text='Click here for file upload or drag and drop.'),

     ),
     html.Div(id='output')
])


@du.callback(
    output=Output('output', 'children'),
    id='upload',
    )
def output(filenames):
    return '<br>'.join(filenames)


if __name__ == '__main__':
    app.run_server(debug=True)