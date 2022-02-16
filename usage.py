from pathlib import Path
import uuid

import dash_uploader as du
import dash

if du.utils.dash_version_is_at_least("2.0.0"):
    from dash import html  # if dash <= 2.0.0, use: import dash_html_components as html
else:
    import dash_html_components as html

from dash.dependencies import Output

app = dash.Dash(__name__)

UPLOAD_FOLDER_ROOT = r"C:\tmp\Uploads"
du.configure_upload(app, UPLOAD_FOLDER_ROOT)


def get_upload_component(id):
    return du.Upload(
        id=id,
        text="Drag and Drop files here",
        text_completed="Completed: ",
        cancel_button=True,
        max_file_size=1800,  # 1800 Mb
        filetypes=["csv", "zip"],
        upload_id=uuid.uuid1(),  # Unique session id
        max_files=10,
    )


def get_app_layout():

    return html.Div(
        [
            html.H1("Demo"),
            html.Div(
                [
                    get_upload_component(id="dash-uploader"),
                    html.Div(id="callback-output"),
                ],
                style={  # wrapper div style
                    "textAlign": "center",
                    "width": "600px",
                    "padding": "10px",
                    "display": "inline-block",
                },
            ),
        ],
        style={
            "textAlign": "center",
        },
    )


# get_app_layout is a function
# This way we can use unique session id's as upload_id's
app.layout = get_app_layout


# 3) Create a callback
@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(n_files, filenames, upload_id, iscompleted, latest_file):

    if n_files == 0:
        return  # no files uploaded yet.

    print(n_files, filenames, upload_id, iscompleted, latest_file)

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        return html.Ul([html.Li(str(x)) for x in out])

    return html.Div("No Files Uploaded Yet!")


if __name__ == "__main__":
    app.run_server(debug=True)
